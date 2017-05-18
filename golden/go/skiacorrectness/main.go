package main

import (
	"flag"
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"runtime/pprof"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"go.skia.org/infra/go/auth"
	"go.skia.org/infra/go/common"
	"go.skia.org/infra/go/database"
	"go.skia.org/infra/go/eventbus"
	"go.skia.org/infra/go/gerrit"
	"go.skia.org/infra/go/git/gitinfo"
	"go.skia.org/infra/go/httputils"
	"go.skia.org/infra/go/issues"
	"go.skia.org/infra/go/login"
	"go.skia.org/infra/go/metadata"
	"go.skia.org/infra/go/rietveld"
	"go.skia.org/infra/go/skiaversion"
	"go.skia.org/infra/go/sklog"
	"go.skia.org/infra/go/timer"
	tracedb "go.skia.org/infra/go/trace/db"
	"go.skia.org/infra/go/util"
	"go.skia.org/infra/golden/go/db"
	"go.skia.org/infra/golden/go/diffstore"
	"go.skia.org/infra/golden/go/digeststore"
	"go.skia.org/infra/golden/go/expstorage"
	"go.skia.org/infra/golden/go/goldingestion"
	"go.skia.org/infra/golden/go/ignore"
	"go.skia.org/infra/golden/go/indexer"
	"go.skia.org/infra/golden/go/search"
	"go.skia.org/infra/golden/go/status"
	"go.skia.org/infra/golden/go/storage"
	"go.skia.org/infra/golden/go/trybot"
	"go.skia.org/infra/golden/go/types"
	gstorage "google.golang.org/api/storage/v1"
)

// Command line flags.
var (
	appTitle           = flag.String("app_title", "Skia Gold", "Title of the deployed up on the front end.")
	authWhiteList      = flag.String("auth_whitelist", login.DEFAULT_DOMAIN_WHITELIST, "White space separated list of domains and email addresses that are allowed to login.")
	cacheSize          = flag.Int("cache_size", 1, "Approximate cachesize used to cache images and diff metrics in GiB. This is just a way to limit caching. 0 means no caching at all. Use default for testing.")
	cpuProfile         = flag.Duration("cpu_profile", 0, "Duration for which to profile the CPU usage. After this duration the program writes the CPU profile and exits.")
	doOauth            = flag.Bool("oauth", true, "Run through the OAuth 2.0 flow on startup, otherwise use a GCE service account.")
	defaultCorpus      = flag.String("default_corpus", "gm", "The corpus identifier shown by default on the frontend.")
	forceLogin         = flag.Bool("force_login", false, "Force the user to be authenticated for all requests.")
	gsBucketNames      = flag.String("gs_buckets", "skia-infra-gm,chromium-skia-gm", "Comma-separated list of google storage bucket that hold uploaded images.")
	imageDir           = flag.String("image_dir", "/tmp/imagedir", "What directory to store test and diff images in.")
	issueTrackerKey    = flag.String("issue_tracker_key", "", "API Key for accessing the project hosting API.")
	local              = flag.Bool("local", false, "Running locally if true. As opposed to in production.")
	memProfile         = flag.Duration("memprofile", 0, "Duration for which to profile memory. After this duration the program writes the memory profile and exits.")
	nCommits           = flag.Int("n_commits", 50, "Number of recent commits to include in the analysis.")
	noCloudLog         = flag.Bool("no_cloud_log", false, "Disables cloud logging. Primarily for running locally.")
	oauthCacheFile     = flag.String("oauth_cache_file", "/home/perf/google_storage_token.data", "Path to the file where to cache cache the oauth credentials.")
	port               = flag.String("port", ":9000", "HTTP service address (e.g., ':9000')")
	promPort           = flag.String("prom_port", ":20000", "Metrics service address (e.g., ':10110')")
	redirectURL        = flag.String("redirect_url", "https://gold.skia.org/oauth2callback/", "OAuth2 redirect url. Only used when local=false.")
	resourcesDir       = flag.String("resources_dir", "", "The directory to find templates, JS, and CSS files. If blank the directory relative to the source code files will be used.")
	rietveldURL        = flag.String("rietveld_url", "https://codereview.chromium.org/", "URL of the Rietveld instance where we retrieve CL metadata.")
	gerritURL          = flag.String("gerrit_url", gerrit.GERRIT_SKIA_URL, "URL of the Gerrit instance where we retrieve CL metadata.")
	storageDir         = flag.String("storage_dir", "/tmp/gold-storage", "Directory to store reproducible application data.")
	gitRepoDir         = flag.String("git_repo_dir", "../../../skia", "Directory location for the Skia repo.")
	gitRepoURL         = flag.String("git_repo_url", "https://skia.googlesource.com/skia", "The URL to pass to git clone for the source repository.")
	serviceAccountFile = flag.String("service_account_file", "", "Credentials file for service account.")
	showBotProgress    = flag.Bool("show_bot_progress", true, "Query status.skia.org for the progress of bot results.")
	traceservice       = flag.String("trace_service", "localhost:10000", "The address of the traceservice endpoint.")
)

const (
	IMAGE_URL_PREFIX = "/img/"

	// OAUTH2_CALLBACK_PATH is callback endpoint used for the Oauth2 flow.
	OAUTH2_CALLBACK_PATH = "/oauth2callback/"
)

func main() {
	defer common.LogPanic()
	var err error

	mainTimer := timer.New("main init")
	// Setup DB flags.
	dbConf := database.ConfigFromFlags(db.PROD_DB_HOST, db.PROD_DB_PORT, database.USER_RW, db.PROD_DB_NAME, db.MigrationSteps())

	// Parse the options. So we can configure logging.
	flag.Parse()

	// Set up the logging options.
	logOpts := []common.Opt{
		common.PrometheusOpt(promPort),
	}

	// Should we disable cloud logging.
	if !*noCloudLog {
		logOpts = append(logOpts, common.CloudLoggingOpt())
	}
	_, appName := filepath.Split(os.Args[0])
	common.InitWithMust(appName, logOpts...)

	v, err := skiaversion.GetVersion()
	if err != nil {
		sklog.Fatalf("Unable to retrieve version: %s", err)
	}
	sklog.Infof("Version %s, built at %s", v.Commit, v.Date)

	// Enable the memory profiler if memProfile was set.
	// TODO(stephana): This should be moved to a HTTP endpoint that
	// only responds to internal IP addresses/ports.
	if *memProfile > 0 {
		time.AfterFunc(*memProfile, func() {
			sklog.Infof("Writing Memory Profile")
			f, err := ioutil.TempFile("./", "memory-profile")
			if err != nil {
				sklog.Fatalf("Unable to create memory profile file: %s", err)
			}
			if err := pprof.WriteHeapProfile(f); err != nil {
				sklog.Fatalf("Unable to write memory profile file: %v", err)
			}
			util.Close(f)
			sklog.Infof("Memory profile written to %s", f.Name())

			os.Exit(0)
		})
	}

	if *cpuProfile > 0 {
		sklog.Infof("Writing CPU Profile")
		f, err := ioutil.TempFile("./", "cpu-profile")
		if err != nil {
			sklog.Fatalf("Unable to create cpu profile file: %s", err)
		}

		if err := pprof.StartCPUProfile(f); err != nil {
			sklog.Fatalf("Unable to write cpu profile file: %v", err)
		}
		time.AfterFunc(*cpuProfile, func() {
			pprof.StopCPUProfile()
			util.Close(f)
			sklog.Infof("CPU profile written to %s", f.Name())
			os.Exit(0)
		})
	}

	// Set the resource directory if it's empty. Useful for running locally.
	if *resourcesDir == "" {
		_, filename, _, _ := runtime.Caller(0)
		*resourcesDir = filepath.Join(filepath.Dir(filename), "../..")
		*resourcesDir += "/frontend"
	}

	// Set up login
	useRedirectURL := *redirectURL
	if *local {
		useRedirectURL = fmt.Sprintf("http://localhost%s/oauth2callback/", *port)
	}
	authWhiteList := metadata.GetWithDefault(metadata.AUTH_WHITE_LIST, login.DEFAULT_DOMAIN_WHITELIST)
	if err := login.Init(useRedirectURL, authWhiteList); err != nil {
		sklog.Fatalf("Failed to initialize the login system: %s", err)
	}

	// Get the client to be used to access GCS and the Monorail issue tracker.
	client, err := auth.NewJWTServiceAccountClient("", *serviceAccountFile, nil, gstorage.CloudPlatformScope, "https://www.googleapis.com/auth/userinfo.email")
	if err != nil {
		sklog.Fatalf("Failed to authenticate service account: %s", err)
	}

	// Get the expecations storage, the filediff storage and the tilestore.
	diffStore, err := diffstore.New(client, *imageDir, strings.Split(*gsBucketNames, ","), diffstore.DEFAULT_GCS_IMG_DIR_NAME, *cacheSize)
	if err != nil {
		sklog.Fatalf("Allocating DiffStore failed: %s", err)
	}

	if !*local {
		if err := dbConf.GetPasswordFromMetadata(); err != nil {
			sklog.Fatal(err)
		}
	}
	vdb, err := dbConf.NewVersionedDB()
	if err != nil {
		sklog.Fatal(err)
	}

	if !vdb.IsLatestVersion() {
		sklog.Fatal("Wrong DB version. Please updated to latest version.")
	}

	digestStore, err := digeststore.New(*storageDir)
	if err != nil {
		sklog.Fatal(err)
	}

	git, err := gitinfo.CloneOrUpdate(*gitRepoURL, *gitRepoDir, false)
	if err != nil {
		sklog.Fatal(err)
	}

	evt := eventbus.New()

	rietveldAPI := rietveld.New(rietveld.RIETVELD_SKIA_URL, httputils.NewTimeoutClient())
	gerritAPI, err := gerrit.NewGerrit(*gerritURL, "", httputils.NewTimeoutClient())
	if err != nil {
		sklog.Fatalf("Failed to create Gerrit client: %s", err)
	}

	// Connect to traceDB and create the builders.
	db, err := tracedb.NewTraceServiceDBFromAddress(*traceservice, types.GoldenTraceBuilder)
	if err != nil {
		sklog.Fatalf("Failed to connect to tracedb: %s", err)
	}

	masterTileBuilder, err := tracedb.NewMasterTileBuilder(db, git, *nCommits, evt, filepath.Join(*storageDir, "cached-last-tile"))
	if err != nil {
		sklog.Fatalf("Failed to build trace/db.DB: %s", err)
	}
	branchTileBuilder := tracedb.NewBranchTileBuilder(db, git, rietveldAPI, gerritAPI, evt)

	ingestionStore, err := goldingestion.NewIngestionStore(*traceservice)
	if err != nil {
		sklog.Fatalf("Unable to open ingestion store: %s", err)
	}
	storages = &storage.Storage{
		DiffStore:         diffStore,
		ExpectationsStore: expstorage.NewCachingExpectationStore(expstorage.NewSQLExpectationStore(vdb), evt),
		MasterTileBuilder: masterTileBuilder,
		BranchTileBuilder: branchTileBuilder,
		DigestStore:       digestStore,
		NCommits:          *nCommits,
		EventBus:          evt,
		TrybotResults:     trybot.NewTrybotResults(branchTileBuilder, rietveldAPI, gerritAPI, ingestionStore),
		RietveldAPI:       rietveldAPI,
		GerritAPI:         gerritAPI,
	}

	// TODO(stephana): Remove this workaround to avoid circular dependencies once the 'storage' module is cleaned up.
	storages.IgnoreStore = ignore.NewSQLIgnoreStore(vdb, storages.ExpectationsStore, storages.GetTileStreamNow(time.Minute))
	if err := ignore.Init(storages.IgnoreStore); err != nil {
		sklog.Fatalf("Failed to start monitoring for expired ignore rules: %s", err)
	}

	// Rebuild the index every two minutes.
	ixr, err = indexer.New(storages, 2*time.Minute)
	if err != nil {
		sklog.Fatalf("Failed to create indexer: %s", err)
	}

	searchAPI, err = search.NewSearchAPI(storages, ixr)
	if err != nil {
		sklog.Fatalf("Failed to create instance of search API: %s", err)
	}

	if !*local {
		*issueTrackerKey = metadata.Must(metadata.ProjectGet(metadata.APIKEY))
	}

	issueTracker = issues.NewMonorailIssueTracker(client)

	statusWatcher, err = status.New(storages)
	if err != nil {
		sklog.Fatalf("Failed to initialize status watcher: %s", err)
	}
	mainTimer.Stop()

	router := mux.NewRouter()

	// Set up the resource to serve the image files.
	imgHandler, err := diffStore.ImageHandler(IMAGE_URL_PREFIX)
	if err != nil {
		sklog.Fatalf("Unable to get image handler: %s", err)
	}
	router.PathPrefix(IMAGE_URL_PREFIX).Handler(imgHandler)

	// New Polymer based UI endpoints.
	router.PathPrefix("/res/").HandlerFunc(makeResourceHandler(*resourcesDir))
	router.HandleFunc(OAUTH2_CALLBACK_PATH, login.OAuth2CallbackHandler)

	// /_/hashes is used by the bots to find hashes it does not need to upload.
	router.HandleFunc("/_/hashes", textAllHashesHandler).Methods("GET")
	router.HandleFunc("/json/version", skiaversion.JsonHandler)
	router.HandleFunc("/loginstatus/", login.StatusHandler)
	router.HandleFunc("/logout/", login.LogoutHandler)

	// json handlers only used by the new UI.
	router.HandleFunc("/json/byblame", jsonByBlameHandler).Methods("GET")
	router.HandleFunc("/json/list", jsonListTestsHandler).Methods("GET")
	router.HandleFunc("/json/paramset", jsonParamsHandler).Methods("GET")
	router.HandleFunc("/json/search", jsonSearchHandler).Methods("GET")
	router.HandleFunc("/json/diff", jsonDiffHandler).Methods("GET")
	router.HandleFunc("/json/details", jsonDetailsHandler).Methods("GET")
	router.HandleFunc("/json/ignores", jsonIgnoresHandler).Methods("GET")
	router.HandleFunc("/json/ignores/add/", jsonIgnoresAddHandler).Methods("POST")
	router.HandleFunc("/json/ignores/del/{id}", jsonIgnoresDeleteHandler).Methods("POST")
	router.HandleFunc("/json/ignores/save/{id}", jsonIgnoresUpdateHandler).Methods("POST")
	router.HandleFunc("/json/triage", jsonTriageHandler).Methods("POST")
	router.HandleFunc("/json/clusterdiff", jsonClusterDiffHandler).Methods("GET")
	router.HandleFunc("/json/cmp", jsonCompareTestHandler).Methods("POST")
	router.HandleFunc("/json/triagelog", jsonTriageLogHandler).Methods("GET")
	router.HandleFunc("/json/triagelog/undo", jsonTriageUndoHandler).Methods("POST")
	router.HandleFunc("/json/trybot", jsonListTrybotsHandler).Methods("GET")
	router.HandleFunc("/json/failure", jsonListFailureHandler).Methods("GET")
	router.HandleFunc("/json/failure/clear", jsonClearFailureHandler).Methods("POST")

	// New endpoints
	router.HandleFunc("/json/newsearch", jsonNewSearchHandler).Methods("GET")

	// For everything else serve the same markup.
	indexFile := *resourcesDir + "/index.html"
	indexTemplate := template.Must(template.New("").ParseFiles(indexFile)).Lookup("index.html")

	// appConfig is injected into the header of the index file.
	appConfig := &struct {
		BaseRepoURL     string `json:"baseRepoURL"`
		DefaultCorpus   string `json:"defaultCorpus"`
		ShowBotProgress bool   `json:"showBotProgress"`
		Title           string `json:"title"`
	}{
		BaseRepoURL:     *gitRepoURL,
		DefaultCorpus:   *defaultCorpus,
		ShowBotProgress: *showBotProgress,
		Title:           *appTitle,
	}

	router.PathPrefix("/").HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/html")

		// Reload the template if we are running locally.
		if *local {
			indexTemplate = template.Must(template.New("").ParseFiles(indexFile)).Lookup("index.html")
		}
		if err := indexTemplate.Execute(w, appConfig); err != nil {
			sklog.Errorln("Failed to expand template:", err)
			return
		}
	})

	// Add the necessary middleware and have the router handle all requests.
	// By structuring the middleware this way we only log requests that are
	// authenticated.
	rootHandler := httputils.LoggingGzipRequestResponse(router)
	if *forceLogin {
		rootHandler = login.ForceAuth(rootHandler, OAUTH2_CALLBACK_PATH)
	}

	// The jsonStatusHandler is being polled, so we exclude it from logging.
	http.HandleFunc("/json/trstatus", jsonStatusHandler)
	http.Handle("/", rootHandler)

	// Start the server
	sklog.Infoln("Serving on http://127.0.0.1" + *port)
	sklog.Fatal(http.ListenAndServe(*port, nil))
}
