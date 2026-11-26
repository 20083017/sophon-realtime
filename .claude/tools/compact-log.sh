#!/usr/bin/env bash
set -euo pipefail

readonly DEFAULT_MAX_LINES=120
readonly MAX_ALLOWED_LINES=10000
readonly MAX_FILTER_BYTES=512

usage() {
	printf 'usage: %s <log-file> [max-lines] [--request REQUEST_ID] [--time TIME_TEXT] [--docker-search]\n' "$0" >&2
}

die() {
	printf 'compact-log: %s\n' "$1" >&2
	exit 2
}

if [ $# -lt 1 ]; then
	usage
	exit 2
fi

LOG_FILE=$1
shift
MAX_LINES=$DEFAULT_MAX_LINES
REQUEST_FILTER=''
TIME_FILTER=''
REQUEST_FILTER_SET=0
TIME_FILTER_SET=0
DOCKER_SEARCH=0

if [ $# -gt 0 ] && [[ $1 != --* ]]; then
	MAX_LINES=$1
	shift
fi

while [ $# -gt 0 ]; do
	case "$1" in
		--request)
			[ "$REQUEST_FILTER_SET" -eq 0 ] || die 'duplicate --request'
			[ $# -ge 2 ] || die 'missing --request value'
			REQUEST_FILTER=$2
			REQUEST_FILTER_SET=1
			shift 2
			;;
		--time)
			[ "$TIME_FILTER_SET" -eq 0 ] || die 'duplicate --time'
			[ $# -ge 2 ] || die 'missing --time value'
			TIME_FILTER=$2
			TIME_FILTER_SET=1
			shift 2
			;;
		--docker-search)
			[ "$DOCKER_SEARCH" -eq 0 ] || die 'duplicate --docker-search'
			DOCKER_SEARCH=1
			shift
			;;
		*)
			die "unknown argument: $1"
			;;
	esac
done

[[ $MAX_LINES =~ ^[1-9][0-9]{0,4}$ ]] &&
	[ "$MAX_LINES" -le "$MAX_ALLOWED_LINES" ] ||
	die "max-lines must be an integer from 1 to $MAX_ALLOWED_LINES"

validate_filter() {
	local name=$1 value=$2
	[ -n "$value" ] || die "$name must not be empty"
	[ "${#value}" -le "$MAX_FILTER_BYTES" ] ||
		die "$name must not exceed $MAX_FILTER_BYTES characters"
	[[ $value != *$'\n'* && $value != *$'\r'* ]] || die "$name must be one line"
}

[ "$REQUEST_FILTER_SET" -eq 0 ] || validate_filter '--request' "$REQUEST_FILTER"
[ "$TIME_FILTER_SET" -eq 0 ] || validate_filter '--time' "$TIME_FILTER"

[ -f "$LOG_FILE" ] || die "log file not found: $LOG_FILE"
[ -r "$LOG_FILE" ] || die "log file is not readable: $LOG_FILE"

if command -v rg >/dev/null 2>&1; then
	SEARCH_TOOL=rg
elif command -v grep >/dev/null 2>&1; then
	SEARCH_TOOL=grep
else
	die 'rg or grep is required'
fi

# The supported legacy severity prefix is one letter followed by an eight-digit date.
# LOGE call sites may still be emitted with an I prefix, so semantic failure and
# stage terms are selected independently instead of matching the macro name.
NATIVE_SEVERITY_PATTERN='^[WEF][0-9]{8} '
BRACKET_SEVERITY_PATTERN='(^|[[:space:]])\[[WEF]\]([[:space:]]|$)'
BUILD_FAILURE_PATTERN='CMake Error|CMake Warning|FAILED:|error:|fatal:|undefined reference|No rule to make target|collect2: error|ld:|Traceback|Exception|segfault|SIGSEGV|SIGABRT'
FAILURE_PATTERN='(^|[^[:alnum:]_])(FAIL|FAILED|FAILURE|ERROR|WARN|FATAL|PANIC|ABORT|INVALID|UNAVAILABLE|REFUSED)([^[:alnum:]_]|$)|watchdog|timed out|timeout'
REQUEST_PATTERN='(request|query)[ _-]?(failed|failure|error|invalid|reject(ed|ion)?|abort(ed)?|drop(ped)?|timeout|timed out|slow|stuck)|(failed|failure|error|invalid|reject(ed|ion)?|abort(ed)?|drop(ped)?|timeout|timed out|slow|stuck)[ _-]?(request|query)'
STAGE_PATTERN='request[ _-]?stage|query[ _-]?stage|dispatch(ed|ing)? request|rewrite request|reject(ed|ing)? request|nlu request|dm request|semantic request|processing[ _-]?stage|pipeline[ _-]?stage'
STARTUP_PATTERN='startup|start-up|starting service|initiali[sz](e|ed|ation)|configuration|configure|config[ _-]?(load|error|fail|invalid|missing)|resource[ _-]?load|model[ _-]?load'
EXTERNAL_PATTERN='external[ _-]?service|upstream|downstream|(^|[^[:alnum:]_])LLM([^[:alnum:]_]|$)|large language model|connection refused'
CACHE_PATTERN='cache|redis|hot[ _-]?fix'
RUNTIME_PATTERN='reset|uart|mcu|queue|drop|reconnect'
INFO_SEMANTIC_TERM_PATTERN='not initialized|query processing|domain|intent|plugin|dialog|task|send chunk|Response=|not exist|failed to load|unregistered|server start|curl|http|response code|failed to request|connection|not hit|matched_rule|(^|[^[:alnum:]_])(cre|rule|context)([^[:alnum:]_]|$)'
INFO_SEMANTIC_PATTERN="^I[0-9]{8} .*($INFO_SEMANTIC_TERM_PATTERN)"
SLOW_REQUEST_PATTERN='End to process request .*cost:[1-9][0-9]{3,}ms'
PATTERN="$NATIVE_SEVERITY_PATTERN|$BRACKET_SEVERITY_PATTERN|$BUILD_FAILURE_PATTERN|$FAILURE_PATTERN|$REQUEST_PATTERN|$STAGE_PATTERN|$STARTUP_PATTERN|$EXTERNAL_PATTERN|$CACHE_PATTERN|$RUNTIME_PATTERN|$INFO_SEMANTIC_PATTERN|$SLOW_REQUEST_PATTERN"

redact() {
	sed -E \
		-e 's/("(password|passwd|token|secret|api[_-]?key|private[_-]?key|authorization)"[[:space:]]*:[[:space:]]*)"[^"]*"/\1"<redacted>"/Ig' \
		-e 's/(Bearer[[:space:]]+)[A-Za-z0-9._~+\/-]+/\1<redacted>/Ig' \
		-e 's/((password|passwd|token|secret|api[_-]?key|private[_-]?key|authorization)[=: ]+)[^[:space:]]+/\1<redacted>/Ig' \
		-e 's#(ssh://)[^@[:space:]]+@#\1<redacted>@#Ig'
}

compact_lines() {
	awk '{ if (length($0) > 240) print substr($0, 1, 240) "... <truncated>"; else print }'
}

first_lines() {
	awk -v max="$MAX_LINES" 'NR <= max { print }'
}

TEMP_INPUT=''
cleanup() {
	[ -z "$TEMP_INPUT" ] || rm -f -- "$TEMP_INPUT"
}
trap cleanup EXIT HUP INT TERM

prepare_docker_search() {
	local line payload

	command -v base64 >/dev/null 2>&1 || die 'base64 is required for --docker-search'
	TEMP_INPUT=$(mktemp "${TMPDIR:-/tmp}/compact-log.docker.XXXXXXXX") ||
		die 'temporary decoded-log creation failed'

	while IFS= read -r line || [ -n "$line" ]; do
		case "$line" in
			LOG_SEARCH\|DATA\|*)
				payload=${line#LOG_SEARCH|DATA|}
				printf '%s' "$payload" | base64 -d >>"$TEMP_INPUT" 2>/dev/null ||
					die 'failed to decode Docker-search data'
				;;
		esac
	done <"$LOG_FILE"
}

SEARCH_FILE=$LOG_FILE
if [ "$DOCKER_SEARCH" -eq 1 ]; then
	prepare_docker_search
	SEARCH_FILE=$TEMP_INPUT
fi

regex_search() {
	local status
	set +e
	if [ "$SEARCH_TOOL" = rg ]; then
		rg -i -n -C 2 -m "$MAX_LINES" -- "$PATTERN" "$SEARCH_FILE"
		status=$?
	else
		grep -E -i -a -n -C 2 -m "$MAX_LINES" -- "$PATTERN" "$SEARCH_FILE"
		status=$?
	fi
	set -e
	[ "$status" -eq 0 ] || [ "$status" -eq 1 ] || return "$status"
	return 0
}

fixed_search() {
	local value=$1 status
	set +e
	if [ "$SEARCH_TOOL" = rg ]; then
		rg -F -n -C 2 -m "$MAX_LINES" -- "$value" "$SEARCH_FILE"
		status=$?
	else
		grep -F -a -n -C 2 -m "$MAX_LINES" -- "$value" "$SEARCH_FILE"
		status=$?
	fi
	set -e
	[ "$status" -eq 0 ] || [ "$status" -eq 1 ] || return "$status"
	return 0
}

collect_regex_context() {
	regex_search 2>/dev/null | redact | compact_lines | first_lines
}

collect_fixed_context() {
	local value=$1
	fixed_search "$value" 2>/dev/null | redact | compact_lines | first_lines
}

print_focus_context() {
	local heading=$1 value=$2 matches
	if ! matches=$(collect_fixed_context "$value"); then
		die "failed to collect $heading"
	fi
	printf '\n### %s\n' "$heading"
	if [ -n "$matches" ]; then
		printf '%s\n' "$matches"
	else
		printf '%s\n' '(no fixed-text matches)'
	fi
}

printf '%s\n' '## Compact Log'
printf 'file: %s\n' "$LOG_FILE"
printf 'size: %s bytes\n\n' "$(wc -c <"$LOG_FILE")"
printf '%s\n' '### Matched failure context'
if ! MATCHES=$(collect_regex_context); then
	die 'failed to collect failure context'
fi
if [ -n "$MATCHES" ]; then
	printf '%s\n' "$MATCHES"
else
	printf '%s\n' '(no failure-pattern matches)'
fi

[ "$REQUEST_FILTER_SET" -eq 0 ] || print_focus_context 'Request context' "$REQUEST_FILTER"
[ "$TIME_FILTER_SET" -eq 0 ] || print_focus_context 'Time context' "$TIME_FILTER"

printf '\n%s\n' '### Last 25 lines'
tail -n 25 "$SEARCH_FILE" | redact | compact_lines
