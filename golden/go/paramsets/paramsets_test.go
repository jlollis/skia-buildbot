package paramsets

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"go.skia.org/infra/go/testutils"
	"go.skia.org/infra/go/tiling"
	"go.skia.org/infra/go/util"
	"go.skia.org/infra/golden/go/tally"
	"go.skia.org/infra/golden/go/types"
)

func TestParamset(t *testing.T) {
	testutils.SmallTest(t)
	tile := &tiling.Tile{
		Traces: map[string]tiling.Trace{
			"a": &types.GoldenTrace{
				Values: []string{"aaa", "bbb"},
				Params_: map[string]string{
					"name":             "foo",
					"config":           "8888",
					types.CORPUS_FIELD: "gm"},
			},
			"b": &types.GoldenTrace{
				Values: []string{"ccc", "ddd", "aaa"},
				Params_: map[string]string{
					"name":             "foo",
					"config":           "565",
					types.CORPUS_FIELD: "gm"},
			},
			"c": &types.GoldenTrace{
				Values: []string{"eee", types.MISSING_DIGEST},
				Params_: map[string]string{
					"name":             "foo",
					"config":           "gpu",
					types.CORPUS_FIELD: "gm"},
			},
			"e": &types.GoldenTrace{
				Values: []string{"xxx", "yyy", "yyy"},
				Params_: map[string]string{
					"name":             "bar",
					"config":           "565",
					types.CORPUS_FIELD: "gm"},
			},
			"f": &types.GoldenTrace{
				Values: []string{"xxx", types.MISSING_DIGEST},
				Params_: map[string]string{
					"name":             "bar",
					"config":           "gpu",
					types.CORPUS_FIELD: "gm"},
			},
		},
	}

	tallies := map[string]tally.Tally{
		"a": {
			"aaa": 1,
			"bbb": 1,
		},
		"b": {
			"ccc": 1,
			"ddd": 1,
			"aaa": 1,
		},
		"c": {
			"eee": 1,
		},
		"e": {
			"xxx": 1,
			"yyy": 2,
		},
		"f": {
			"xxx": 1,
		},
		"unknown": {
			"ccc": 1,
			"ddd": 1,
			"aaa": 1,
		},
	}

	byTrace := byTraceForTile(tile, tallies)

	// Test that we are robust to traces appearing in tallies, but not in the tile, and vice-versa.
	assert.Equal(t, byTrace["foo"]["bbb"]["config"], []string{"8888"})
	assert.Equal(t, byTrace["foo"]["aaa"]["name"], []string{"foo"})
	assert.Equal(t, byTrace["bar"]["yyy"]["config"], []string{"565"})
	assert.Equal(t, util.NewStringSet([]string{"565", "gpu"}), util.NewStringSet(byTrace["bar"]["xxx"]["config"]))
	assert.Equal(t, util.NewStringSet([]string{"565", "8888"}), util.NewStringSet(byTrace["foo"]["aaa"]["config"]))
	assert.Nil(t, byTrace["bar:fff"])
}
