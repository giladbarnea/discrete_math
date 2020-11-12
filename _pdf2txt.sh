#!/usr/bin/env zsh
function dowork() {
	find . -type f -regex ".*/.*\.pdf" | while read file; do
		bytes=$(stat -c "%s" "$file")
		mb=$(echo "$bytes / 1000000" | bc -l)
		mb_round=$(cut -c 1-5 <<<$mb)
		if [[ "$mb_round" = "."* ]]; then
			kb=$(echo "$bytes / 1000" | bc -l)
			kb_round=$(cut -c 1-5 <<<$kb)
			size_str="$kb_round KB"
		else
			size_str="$mb_round MB"
		fi

		echo "$file ($size_str)"
		pdftotext -layout "$file"
	done
}
dowork