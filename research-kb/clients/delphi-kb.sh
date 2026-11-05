#!/bin/sh
# Delphi has no MCP client. These wrappers are what `research-kb install-client
# --client delphi` writes to ~/.local/bin, kept here as a readable template.
#
# delphi-kb        prints a citation-bearing context pack
# delphi-kb-ask    sends that pack to `delphi ask` as the prompt
set -eu
export RESEARCH_KB_HOME=${RESEARCH_KB_HOME:-/absolute/shared/research-kb-data}
export RESEARCH_KB_CONFIG=${RESEARCH_KB_CONFIG:-/absolute/path/to/sources.toml}
RESEARCH_KB=${RESEARCH_KB:-/absolute/path/to/research-kb}

query=${1:?usage: delphi-kb "research question" [--repo NAME]}
shift || true
exec "$RESEARCH_KB" brief "$query" "$@"
