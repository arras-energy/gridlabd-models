#!/bin/sh
#
# ICA Analysis
#
# Environment:
#
#   OPENFIDO_INPUT --> input folder when MDB files are placed
#   OPENFIDO_OUTPUT --> output folder when CSV files are placed
#
# Special files:
#
#   config.csv -> run configuration
#
#     MODELNAME,<modelname> --> (optional) input file name in OPENFIDO_INPUT folder (default *.glm)
#     GLMCONFIG,<configname> --> (optional) configuration file to load prior to loading the model (default "config.glm")
#     GLMRECORD,<recordername> --> (optional) recorder file to load after loading the model (default "recorders.glm")
#     TEMPLATE,<gitname> --> (optional) GitHub template name to use (default "ica_analysis.glm")
#     <template-configvar>,<value> --> (optional) GridLAB-D template configuration variable (see "gridlabd template config" for details)
#
VERSION=0
EXECPATHNAME=$0
if [ "${EXECPATHNAME##/*}" != "" ]; then
	EXECPATH="$PWD"
	EXECNAME=$EXECPATHNAME
else
	EXECPATH=${EXECPATHNAME%/*}
	EXECNAME=${EXECPATHNAME##*/}
fi
OPENFIDO_INIT="$EXECPATH/src/openfido-init.sh"
OPENFIDO_RUN="$EXECPATH/src/openfido-run.sh"

#
# Exit codes
#
E_INTERNAL=1 # internal error
E_NOTFOUND=2 # file not found
E_REQUIRED=3 # requirement not satisfied
E_INSTALL=4 # install failure
E_DOWNLOAD=5 # download failure
E_CONVERT=6 # conversion failure

#
# Error handling
#
TMP=/tmp/openfido-$$
OLDWD=${PWD}
LINENO="?"
CONFIG="${OPENFIDO_INPUT}/config.csv"
STDOUT="${OPENFIDO_OUTPUT}/stdout"
STDERR="${OPENFIDO_OUTPUT}/stderr"
trap 'onexit $0 ${LINENO} $?' EXIT
onexit()
{
	cd $OLDWD
	rm -rf $TMP
	if [ $3 -ne 0 -a $# -gt 3 ]; then
		echo "*** ERROR $3 ***"
		grep -v '^+' ${STDERR}
		echo "  $1($2): see ${STDERR} output for details"
	fi

	# show input files
	debug "Output files:"
	[ "${OPENFIDO_DEBUG:-no}" = "yes" ] && ls -l ${OPENFIDO_OUTPUT} | sed '1,$s/^/* /'

	if [ $3 -eq 0 ]; then
		debug "Completed $1 at $(date)"
	else
		echo "Failed $1 at $(date) (see ${STDERR} for details)"
	fi

	exit $3
}
error()
{
	XC=$1
	shift 1
	echo "*** ERROR $XC ***" 
	echo "  $* " 
	exit $XC
}
warning()
{
	echo "WARNING [${EXECNAME}:${LINENO}]: $*" 
}
debug()
{
	if [ "${OPENFIDO_DEBUG:-no}" = "yes" ]; then
		echo $*
	fi
}
require()
{
	for VAR in $*; do
		test ! -z "$(printenv ${VAR})" || error $E_REQUIRED "Required value for ${VAR} not specified in ${CONFIG}"
	done
}
default()
{
	VAR="$1"
	if [ -z "$(printenv ${VAR})" ]; then
		shift 1
		export ${VAR}="$*"
	fi
}
getconfig()
{
	if [ ! -f "${CONFIG}" ]; then
		export $1="$2"
	else
		export $1=$(grep ^$1, "${CONFIG}" | cut -f2 -d,)
		if [ -z "$(printenv $1)" -a $# -eq 2 ]; then
			default $1 $2
		else
			require $1
		fi
	fi
}

# nounset: undefined variable outputs error $message, and forces an exit
set -u

# errexit: abort script at first error
set -e

# print command to stderr before executing it:
set -x

# path to source folder
if [ "$0" = "openfido.sh" ]; then
	SRCDIR=$PWD
else
	SRCDIR=$(cd $(echo "$0" | sed "s/$(basename $0)\$//") ; pwd )
fi

# startup notice
debug "Starting $0 at $(date) in ${SRCDIR}"

# install required tools
if [ "${OPENFIDO_AUTOINSTALL:-yes}" == "yes" -a -f "install.txt" ]; then
	UNAME=$(uname -s)
	if [ "${UNAME}" == "Darwin" ]; then
		if [ ! -z "$(which brew)" ]; then
			INSTALL="brew install -q"
			brew update 1>/dev/stderr || error $E_INSTALL "unable to update brew"
		else
			INSTALL=false
		fi
	elif [ "${UNAME}" == "Linux" ]; then
		if [ ! -z "$(which apt)" ]; then
			INSTALL="apt install -yqq"
			apt update -y 1>/dev/stderr || error $E_INSTALL "unable to update apt"
		elif [ ! -z "(which yum)" ]; then
			INSTALL="yum install -yqq"
			yum update -y 1>/dev/stderr || error $E_INSTALL "unable to update yum"
		else
			INSTALL="false"
		fi
	else
		INSTALL="false"
	fi
	for TOOL in $(cat "install.txt");  do
		NAME=$(echo $TOOL | cut -f1 -d:)
		CODE=$(echo $TOOL | cut -f2 -d:)
		if [ -z "$(which ${NAME})" ]; then
			debug "Installing ${TOOL}"
			${INSTALL} ${CODE} 1>/dev/stderr || error $E_INSTALL "unable to install tool '${TOOL}' specified in 'install.txt'"
		fi
	done
fi

# work in new temporary directory
rm -rf "$TMP"
mkdir -p "$TMP"
cd "$TMP"
debug '* ' "TMP = ${TMP} (working folder)"

# pipeline initialization
[ -f "${OPENFIDO_INIT}" ] && . ${OPENFIDO_INIT} || error $E_INTERNAL "${OPENFIDO_INIT} failed"

# display environment information
debug "Environment settings:"
debug '* ' "OPENFIDO_INPUT = $OPENFIDO_INPUT"
debug '* ' "OPENFIDO_OUTPUT = $OPENFIDO_OUTPUT"

debug "Config settings:"
for NAME in $(printenv | grep '^DEFAULT_' | cut -f1 -d= ) ${DEFAULT_VARLIST}; do
	debug '* ' "$NAME = $(printenv $NAME)"
done

# requirements
if [ "${NOINSTALL:-no}" == "yes" ]; then
	if [ -f "requirements.txt" ]; then
		python3 -m pip install -r "requirements.txt" || error $E_INSTALL "unable to satisfy system 'requirements.txt'"
	fi
	if [ -f "${OPENFIDO_INPUT}/requirements.txt" ]; then
		python3 -m pip install -r "${OPENFIDO_INPUT}/requirements.txt" || error $E_INSTALL "unable to satisfy user 'requirements.txt'"
	fi
fi

# show input files
debug "Input files:"
[ "${OPENFIDO_DEBUG:-no}" = "yes" ] && ls -l ${OPENFIDO_INPUT} | sed '1,$s/^/* /'

# perform the main run
. ${OPENFIDO_RUN} || error $E_INTERNAL "${OPENFIDO_RUN} failed"
