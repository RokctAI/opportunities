#!/usr/bin/env bash
# Copyright (c) 2026 ROKCT INTELLIGENCE (PTY) LTD
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# Moves the OCDS archive between a local directory and GitHub Release
# assets, so the data never enters git history.
#
# Layout:
#   ocds-YYYY   one release per year (2021+), holding releases-YYYY-MM.jsonl.gz.
#               Pre-release while the year is running; promoted to a full
#               release once the year has ended. Assets stay updatable, so
#               late awards still land after promotion.
#   ocds-index  always a pre-release: manifest.json, ocids.txt.gz,
#               releases-pre2021.jsonl.gz, releases-unknown-date.jsonl.gz.
#
# Usage (needs gh with a token that can write releases):
#   release_assets.sh download DIR   # fetch all assets (bootstraps from git if absent)
#   release_assets.sh upload DIR     # push changed/removed assets, create/promote releases

set -euo pipefail

cmd=${1:?download|upload}
dir=${2:?data dir}
state="$dir/.before.sha"
index_tag=ocds-index

tag_for() {
	case "$1" in
	releases-[0-9][0-9][0-9][0-9]-[0-9][0-9].jsonl.gz) echo "ocds-${1:9:4}" ;;
	*) echo "$index_tag" ;;
	esac
}

ocds_tags() {
	gh release list --limit 200 --json tagName -q '.[].tagName' | grep -E '^ocds-' || true
}

checksums() {
	(cd "$dir" && find . -maxdepth 1 -type f ! -name '.*' -printf '%f\n' | sort | xargs -r sha256sum | sort)
}

ensure_release() {
	local tag=$1 title notes
	gh release view "$tag" >/dev/null 2>&1 && return 0
	if [ "$tag" = "$index_tag" ]; then
		title="eTenders OCDS archive: index"
		notes="Manifest, ocid index and legacy/undated records for the eTenders OCDS archive. Updated in place by the OCDS Archive Sync workflow; see ocds/README.md."
	else
		title="eTenders OCDS archive: ${tag#ocds-}"
		notes="Every eTenders OCDS release dated ${tag#ocds-}, one gzipped JSONL file per month. Pre-release while the year is running, a full release once it has ended; late awards are still added in place. See ocds/README.md."
	fi
	gh release create "$tag" --prerelease --latest=false --title "$title" --notes "$notes"
}

download() {
	mkdir -p "$dir"
	local tags
	tags=$(ocds_tags)
	if [ -z "$tags" ]; then
		# Bootstrap: the archive was committed to git (PR #100) until it moved
		# to release assets; restore it from the last commit that still had it.
		local del
		del=$(git rev-list -1 HEAD -- ocds/manifest.json)
		git archive "${del}^" ocds/ | tar -x -C "$dir" --strip-components=1 \
			--wildcards 'ocds/*.gz' 'ocds/manifest.json'
		: >"$state"
	else
		for t in $tags; do
			gh release download "$t" --dir "$dir" --clobber
		done
		checksums >"$state"
	fi
	echo "downloaded $(find "$dir" -maxdepth 1 -type f ! -name '.*' | wc -l) files"
}

upload() {
	local changed n=0
	changed=$(comm -13 "$state" <(checksums) | awk '{print $2}')
	for f in $changed; do
		local tag
		tag=$(tag_for "$f")
		ensure_release "$tag"
		gh release upload "$tag" "$dir/$f" --clobber
		n=$((n + 1))
	done
	echo "uploaded $n assets"

	local year
	year=$(date -u +%Y)
	for t in $(ocds_tags); do
		for a in $(gh release view "$t" --json assets -q '.assets[].name'); do
			[ -e "$dir/$a" ] || gh release delete-asset "$t" "$a" --yes
		done
		if [[ $t =~ ^ocds-([0-9]{4})$ ]] && [ "${BASH_REMATCH[1]}" -lt "$year" ] &&
			[ "$(gh release view "$t" --json isPrerelease -q .isPrerelease)" = "true" ]; then
			gh release edit "$t" --prerelease=false --latest=false
			echo "promoted $t to a full release"
		fi
	done
}

case "$cmd" in
download) download ;;
upload) upload ;;
*)
	echo "unknown command: $cmd" >&2
	exit 2
	;;
esac
