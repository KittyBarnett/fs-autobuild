#!/usr/bin/env python

import os
import sys
import common

# for the time being, we expect that we're checked out side-by-side with
# parabuild buildscripts, so back up a level to find $helper.
helper = os.path.join(os.path.dirname(__file__),
                      os.pardir,
                      os.pardir,
                      'buildscripts/hg/bin')
# Append helper to sys.path.
_helper_idx = len(sys.path)
sys.path.append(helper)
assert sys.path[_helper_idx] == helper

get_params = None
try:
    import get_params
    print >>sys.stderr, "found get_params: '%s'" % get_params.__file__
except ImportError:
    pass
# *TODO - restor original sys.path value

environment_template = """
    export autobuild="%(AUTOBUILD_EXECUTABLE_PATH)s"
    export AUTOBUILD_VERSION_STRING="%(AUTOBUILD_VERSION_STRING)s"
    export AUTOBUILD_PLATFORM="%(AUTOBUILD_PLATFORM)s"
    upload_item () {
        # back-compat wrapper for parbuild buildscripts
        local item_type="$1"
        local item="$2"
        local encoding="$3"
        local asset_urls="${4:-"$build_log_dir"/asset_urls}"
        local asset_name="$5"

        # *TODO - delegate this properly to 'autobuild upload'
        "$autobuild" upload "$item"
    }
    fail () {
        echo "BUILD FAILED"
        exit 1
    }
    pass () {
        echo "BUILD SUCCEEDED"
    }

    # imported build-lindenlib functions
    fetch_archive() {
        local url=$1
        local archive=$2
        local md5=$3
        if ! [ -r "$archive" ] ; then
            curl -L -o "$archive" "$url"                    || return 1
        fi
        if [ "$AUTOBUILD_PLATFORM" == "darwin" ] ; then
            test "$md5 $archive" == "$(md5 -r "$archive")"
        else
            echo "$md5 *$archive" | md5sum -c
        fi
    }
    extract () {
        # Use a tar command appropriate to the extension of the filename passed as
        # $1. If a subsequent update of a given tarball changes compression types,
        # this should hopefully avoid having to go through this script to update
        # the tar switches to correspond to the new file type.
        switch="-x"
        # Decide whether to specify -xzvf or -xjvf based on whether the archive
        # name ends in .tar.gz or .tar.bz2.
        if [ "${1%%.tar.gz}" != "$1" ]
        then switch="${switch}z"
        elif [ "${1%%.tar.bz2}" != "$1" ]
        then switch="${switch}j"
        fi
        switch="${switch}vf"
        tar "$switch" "$1" || exit 1
    }

    MAKEFLAGS="%(MAKEFLAGS)s"
    DISTCC_HOSTS="%(DISTCC_HOSTS)s"
"""

import autobuild_base

class autobuild_tool(autobuild_base.autobuild_base):
    def get_details(self):
        return dict(name=self.name_from_file(__file__),
                    description='Prints out the shell environment Autobuild-based buildscripts to use (by calling \'eval\').')
    
    # called by autobuild to add help and options to the autobuild parser, and by
    # standalone code to set up argparse
    def register(self, parser):
        parser.add_argument('-v', '--version', action='version', version='source_environment tool module 1.0')

    def run(self, args):
        print environment_template % {
                'AUTOBUILD_EXECUTABLE_PATH':sys.argv[0],
                'AUTOBUILD_VERSION_STRING':"0.0.1-mvp",
                'AUTOBUILD_PLATFORM':common.get_current_platform(),
                'MAKEFLAGS':"",
                'DISTCC_HOSTS':"",
            }

        if get_params:
            # *TODO - run get_params.generate_bash_script()
            pass
