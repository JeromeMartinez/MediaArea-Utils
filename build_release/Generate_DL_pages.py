#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import sys
import os
import subprocess
import fnmatch

print "\n========================================================"
print "Generate_DL_pages.py"
print "Copyright (c) MediaArea.net SARL. All Rights Reserved."
print "Use of this source code is governed by a BSD-style"
print "license that can be found in the License.txt file in the"
print "root of the source tree."
print "========================================================\n"

##################################################################
class mysql:

    def __init__(self):
        self.running = True
        try:
            self.sql = MySQLdb.connect(
                    host=HOR_config["MySQL_host"],
                    user=HOR_config["MySQL_user"],
                    passwd=HOR_config["MySQL_passwd"],
                    db=HOR_config["MySQL_db"])
        except MySQLdb.Error, e:
            self.running = True
            print "*** MySQL Error %d: %s ***" % (e.args[0], e.args[1])
            print "*** FATAL: quitting ***"
            sys.exit(1)

    def execute(self, query):
        self.cursor = self.sql.cursor()
        self.cursor.execute(query)
        self.open = True

    def rowcount(self):
        if self.open:
            return self.cursor.rowcount
        else:
            print "*** rowcount: No DB cursor is open! ***"
            return 0

    def fetchone(self):
        if self.open:
            return self.cursor.fetchone()
        else:
            print "*** fetchone: No DB cursor is open! ***"
            return 0

    def fetchall(self):
        if self.open:
            return self.cursor.fetchall()
        else:
            print "*** fetchall: No DB cursor is open! ***"
            return 0

    def closecursor(self):
        if self.open:
            self.sql.commit()
            return self.cursor.close()
        else:
            print "*** close: No DB cursor is open! ***"
            return 0

    def close(self):
        if self.open:
            self.sql.commit()
            return self.cursor.close()
        else:
            print "*** close: No DB cursor is open! ***"
            return 0

##################################################################
#def Commit():
#
#    if fnmatch.fnmatch(OBS_Package, "MediaConch*"):
#        subprocess.call(["rm -fr /tmp/MediaConch"], shell=True)
#        # 430 Mo through git every runtime: thanks but no thanks
#        #subprocess.call(["cp -r ~/MediaConch /tmp/"], shell=True)
#        #subprocess.call(["cd /tmp/MediaConch ; git pull --rebase"], shell=True)
#        subprocess.call(["git clone https://github.com/MediaArea/MediaConch.git /tmp/MediaConch"], shell=True)
#        subprocess.call(["cd /tmp/MediaConch ; git checkout -b gh-pages origin/gh-pages"], shell=True)
#        dl_files_dir = "/tmp/MediaConch/downloads"
#        
#    #if OBS_Package == "MediaInfo" or fnmatch.fnmatch(OBS_Package, "MediaInfo_*"):

##################################################################
def DL_pages(OS_name):
    
    print "Generating " + Project.upper() + " download pages for " + OS_name
    print

    Skeletons_path = Script_emplacement + "/dl_templates/" + Project.upper() + "_" + OS_name
    OS_title = Config[ Project.upper() + "_" + OS_name + "_title" ]

    Header_file_path = Skeletons_path + "_header"
    Header_file = open(Header_file_path, "r")
    Header = Header_file.read()
    Header_file.close()

    Filename = Config[ Project.upper() + "_" + OS_name + "_filename" ]
    Destination = open("/tmp/" + Project + "_dl_pages/" + Filename, "w")
    Destination.write(Header)

    Template_file_path = Skeletons_path + "_template"
    Template_file = open(Template_file_path, "r")
    Content = Template_file.read()
    Template_file.close()

    if Project == "mi" and OS_name == "mac":
        Content = Content.replace("VERSIONS_APPLESTORE", Config[ Project.upper() + "_" + OS_name + "_applestore" ])

    Content = Content.replace(Project.upper() + "_VERSION", Project_version)
    Content = Content.replace("MIL_VERSION", MIL_version)
    Content = Content.replace("OS_TITLE", OS_title)

    Destination.write(Content + "\n")
    Destination.write("</tbody>\n</table>\n")
    if Project == "mi":
        Destination.write("</body>\n</html>\n")
    Destination.close()

##################################################################
def Sources():
    
    print "Generating " + Project.upper() + " download pages for sources"
    print

    Skeletons_path = Script_emplacement + "/dl_templates/" + Project.upper() + "_sources"

    Header_file_path = Skeletons_path + "_header"
    Header_file = open(Header_file_path, "r")
    Header = Header_file.read()
    Header_file.close()

    Filename = Config[ Project.upper() + "_sources_filename" ]
    Destination = open("/tmp/" + Project + "_dl_pages/" + Filename, "w")
    Destination.write(Header)

    Template_file_path = Skeletons_path + "_template"
    Template_file = open(Template_file_path, "r")
    Content = Template_file.read()
    Template_file.close()

    Content = Content.replace(Project.upper() + "_VERSION", Project_version)
    Content = Content.replace("MIL_VERSION", MIL_version)
    Content = Content.replace("ZL_VERSION", ZL_version)

    Destination.write(Content + "\n")
    Destination.write("</tbody>\n</table>\n")
    if Project == "mi":
        Destination.write("</body>\n</html>\n")
    Destination.close()

##################################################################
def OBS():

    print "Generating " + Project.upper() + " download pages for linux"
    print

    # Open the access to the DB
    Cursor = mysql()

    Table_releases_dlpages = "`releases_dlpages_" + Project + "`"
    Table_releases_obs = "`releases_obs_" + Project + "`"

    # Fetch the current version of MC|MI
    Cursor.execute("SELECT version FROM " + Table_releases_dlpages + " INNER JOIN " + Table_releases_obs + " ON " + Table_releases_dlpages + ".platform = " + Table_releases_obs + ".distrib WHERE " + Table_releases_obs + ".state = 1;")
    Result = Cursor.fetchone()
    if Result != None:
        Version = Result[0]
    else:
        print "ERROR, no infos on succeeded distribs in the DB."
        print "All builds have failed on OBS?"
        print
        sys.exit(1)

    Active_distribs = []
    # We use a dictionnary even if unordered, because:
    # “TypeError: list indices must be integers, not str”
    Sorted_releases = {}

    Cursor.execute("SELECT * FROM " + Table_releases_dlpages + ";")
    DB_distribs = Cursor.fetchall()

    for DB_dist in DB_distribs:

        Distrib = DB_dist[0]
        # Separate the distrib name of the release number
        Distrib_name = Distrib.split("_", 1)[0]
        Release_name = Distrib.split("_", 1)[1]

        # Build a list with the names of the active distribs, ie
        # with a download page to generate
        if not Distrib_name in Active_distribs:
            Active_distribs.append(Distrib_name)

        # The release(s) who build on OBS
        if not Distrib_name in Sorted_releases:
            # Sorted_releases[Distrib_name] will be a pair
            # [Release_name, Status].
            Sorted_releases[Distrib_name] = []

        # Verify if Release_name is already present in the
        # dictionnary Sorted_releases
        Already_here = False
        # If the list is empty, can’t be in it
        if len(Sorted_releases[Distrib_name]) > 0:
            Count = 0
            for i in Sorted_releases[Distrib_name]:
                # The release name is at the first place (index 0)
                # in the list Sorted_releases[Distrib_name][]
                if Release_name == Sorted_releases[Distrib_name][Count][0]:
                    Already_here = True
                # "i" is a list, so we need a counter to access
                # it’s content by index
                Count = Count + 1

        # If not present in Sorted_releases, append it and mark the
        # status "current" or "old", whether it build or not for
        # the current version of MC
        if not Already_here:
            Cursor.execute("SELECT version FROM " + Table_releases_dlpages + " WHERE platform = '" + Distrib + "';")
            DB_version = Cursor.fetchone()[0]
            if DB_version == Version:
                Status = "current"
            else:
                Status = "old"
            Sorted_releases[Distrib_name].append([Release_name, Status])

    # Sort the version numbers of the releases
    for Distrib in Sorted_releases:
        Sorted_releases[Distrib].sort()
        Sorted_releases[Distrib].reverse()

    # Specific sorting for openSUSE
    Opensuse_releases = []
    for Status in ['current', 'old']:
        # 1. current Leap release
        Count = 0
        for Release_infos in Sorted_releases["openSUSE"]:
            # The .replace(" ", "_") is for "Leap XX" vs "Leap_XX"
            if Release_infos[0] == Config["opensuse_current_release"].replace(" ", "_") and Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
                del Sorted_releases["openSUSE"][Count]
            Count = Count + 1
        # 2. Tumbleweed
        Count = 0
        for Release_infos in Sorted_releases["openSUSE"]:
            if Release_infos[0] == "Tumbleweed" and Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
                del Sorted_releases["openSUSE"][Count]
            Count = Count + 1
        # 3. Factory
        Count = 0
        for Release_infos in Sorted_releases["openSUSE"]:
            if Release_infos[0] == "Factory" and Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
                del Sorted_releases["openSUSE"][Count]
            Count = Count + 1
        # 4. Factory ARM
        Count = 0
        for Release_infos in Sorted_releases["openSUSE"]:
            if Release_infos[0] == "Factory_ARM" and Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
                del Sorted_releases["openSUSE"][Count]
            Count = Count + 1
        # 5. Other Leap releases
        Count = 0
        for Release_infos in Sorted_releases["openSUSE"]:
            if fnmatch.fnmatch(Release_infos[0], "Leap*") and Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
                del Sorted_releases["openSUSE"][Count]
            Count = Count + 1
        # 6. All other releases
        for Release_infos in Sorted_releases["openSUSE"]:
            if Release_infos[1] == Status:
                Opensuse_releases.append(Release_infos)
    # Put the sorted list back in the dictionnary
    Sorted_releases["openSUSE"] = Opensuse_releases

    # Verbose mode
    #print Sorted_releases

    for Distrib_name in Active_distribs:
        Distrib_name_lower = Distrib_name.lower()
        if Distrib_name_lower == "xubuntu":
            Distrib_name_lower = "ubuntu"
    
        # Verbose mode
        #print

        if Distrib_name == "Debian" or Distrib_name == "xUbuntu":
            Package_type = "deb"
        if Distrib_name == "RHEL" or Distrib_name == "CentOS" or Distrib_name == "Fedora":
            Package_type = "rpm"
            Package_infos[Package_type]["i586"] = "i686"
        if Distrib_name == "SLE" or Distrib_name == "openSUSE" or Distrib_name == "Mageia":
            Package_type = "rpm"
            Package_infos[Package_type]["i586"] = "i586"

        Header_file_path = Script_emplacement + "/dl_templates/" + Project.upper() + "_" + Distrib_name_lower + "_header"
        Header_file = open(Header_file_path, "r")
        Header = Header_file.read()
        Header_file.close()
    
        if Project == "mc":
            Filename = Distrib_name_lower + ".md"
        if Project == "mi":
            if Distrib_name == "xUbuntu":
                Filename = "Ubuntu.html"
            else:
                Filename = Distrib_name + ".html"

        Destination = open("/tmp/" + Project + "_dl_pages/" + Filename, "w")
        Destination.write(Header)

        # Build the list of the releases for a distrib

        for Release_infos in Sorted_releases[Distrib_name]:

            Release_name = Release_infos[0]
            Release_status = Release_infos[1]
            Release_in_config_file = Distrib_name_lower + "_" + Release_name.lower().replace(".", "_")
            Release_title = Config[ Release_in_config_file + "_title" ]

            # Verbose mode
            #print Distrib_name + " " + Release_name

            Release_with_server = False
            if Project == "mc":
                Cursor.execute("SELECT servername FROM " + Table_releases_dlpages + " WHERE platform = '" + Distrib_name + "_" + Release_name + "';")
                Result = Cursor.fetchone()
                if Result != None and Result[0] != "":
                    Release_with_server = True

            Release_with_wx = False
            if Project == "mi" and (Distrib_name == "RHEL" or Distrib_name == "CentOS"):
                # The second if is mandatory (<distrib>_<release>_wx only exists for RHEL/CentOS).
                if Config[ Release_in_config_file + "_wx" ] != "":
                    Release_with_wx = True

            Rowspan = 4
            if Release_with_server == True:
                Rowspan = Rowspan + 1
            if Release_with_wx == True:
                Rowspan = Rowspan + 1
            Arch_rowspan = str(Rowspan)

            Cursor.execute("SELECT arch FROM " + Table_releases_dlpages + " WHERE platform = '" + Distrib_name + "_" + Release_name + "';")
            Result = Cursor.fetchall()
            DB_archs = []
            DB_archs = Result
            Number_of_archs = len(DB_archs)
            Release_rowspan = Number_of_archs * Rowspan
            # For the link to RHEL7 ppc64
            if Distrib_name + Release_name == "CentOS7":
                Release_rowspan = Release_rowspan + 1
            Release_rowspan_number = str(Release_rowspan)

            # Sort the archs : x64_64, i586, arm, ppc64
            Archs = []
            for DB_arch in DB_archs:
                if DB_arch[0] == "x86_64":
                    Archs.append("x86_64")
            for DB_arch in DB_archs:
                if DB_arch[0] == "i586":
                    Archs.append("i586")
            for DB_arch in DB_archs:
                if DB_arch[0] == "armv6l":
                    Archs.append("armv6l")
            for DB_arch in DB_archs:
                if DB_arch[0] == "armv7l":
                    Archs.append("armv7l")
            for DB_arch in DB_archs:
                if DB_arch[0] == "aarch64":
                    Archs.append("aarch64")
            for DB_arch in DB_archs:
                if DB_arch[0] == "ppc64":
                    Archs.append("ppc64")

            # Build the list of the archs for a release

            Count = 0

            for Arch in Archs:

                if Release_with_server == True:
                    Template_file_path = Script_emplacement + "/dl_templates/MC_linux_template"
                elif Project == "mc":
                    Template_file_path = Script_emplacement + "/dl_templates/MC_linux_template_no_server"
                elif Project == "mi":
                    Template_file_path = Script_emplacement + "/dl_templates/MI_linux_template"
                Template_file = open(Template_file_path, "r")
                Content = Template_file.read()
                Template_file.close()

                Release_name_formated = Release_name
                if Distrib_name == "Debian":
                    Release_name_formated = Release_name.replace(".0", "")

                Count = Count + 1
                if Count == 1:
                    Release_rowspan = "\n    <th rowspan=\"" + Release_rowspan_number + "\" id=\"" + Release_name_formated + "\">" + Release_title + "</th>"
                else:
                    Release_rowspan = ""
                Content = Content.replace("RELEASE_ROWSPAN", Release_rowspan)
                
                if Release_status == "old":
                    Release_class = " class=\"old-files\""
                else:
                    Release_class = ""
                Content = Content.replace("RELEASE_CLASS", Release_class)

                Content = Content.replace("ARCH_ROWSPAN", Arch_rowspan)
                Content = Content.replace("RELEASE_VERSION", Release_name_formated)
                Content = Content.replace("RELEASE_ARCH", Package_infos[Package_type][Arch])

                Request = "SELECT version, cliname, clinamedbg, guiname, guinamedbg"
                if Project == "mc":
                    Request = Request + ", servername, servernamedbg"
                Request = Request + " FROM " + Table_releases_dlpages \
                        + " WHERE platform = '" + Distrib_name + "_" + Release_name + "'" \
                        + " AND arch = '" + Arch + "';"
                Cursor.execute(Request)
                Result = Cursor.fetchone()
                if Result != None:
                    Project_version = Result[0]
                    Cli_name = Result[1]
                    Cli_name_dbg = Result[2]
                    Gui_name = Result[3]
                    Gui_name_dbg = Result[4]
                    if Project == "mc":
                        Server_name = Result[5]
                        Server_name_dbg = Result[6]
                else:
                    print
                    print "ERROR: can’t read the infos about " + Project.upper() + " in the DB for " + Distrib_name + " " + Release_name
                    print
                    sys.exit(1)

                Content = Content.replace(Project.upper() + "_VERSION", Project_version)
                Content = Content.replace("CLI_PACKAGE", Cli_name)
                if Release_with_server == True:
                    Content = Content.replace("SERVER_PACKAGE", Server_name)
                Content = Content.replace("GUI_PACKAGE", Gui_name)

                Cursor.execute("SELECT" \
                        + " version, libname, libnamedbg, libnamedev" \
                        + " FROM `releases_dlpages_mil`" \
                        + " WHERE platform = '" + Distrib_name + "_" + Release_name + "'" \
                        + " AND arch = '" + Arch + "';")
                Result = Cursor.fetchone()
                if Result != None:
                    MIL_version = Result[0]
                    MIL_lib_name = Result[1]
                    MIL_lib_name_dbg = Result[2]
                    MIL_lib_name_dev = Result[3]

                    Content = Content.replace("MIL_VERSION", MIL_version)
                    Content = Content.replace("MIL_PACKAGE", MIL_lib_name)

                    if Project == "mi" \
                    and (Distrib_name + "_" + Release_name == "CentOS_4" \
                    or Distrib_name + "_" + Release_name == "RHEL_4" \
                    or Distrib_name + "_" + Release_name == "Debian_4.0") \
                    or Distrib_name == "Arch" :
                        MIL_dev_package = ""
                    else:
                        MIL_dev_package = " <small>(<a href=\"https://mediaarea.net/download/binary/libmediainfo0/" + MIL_version + "/" + MIL_lib_name_dev + "\">devel</a>)</small>"
                    Content = Content.replace("MIL_DEV_PACKAGE", MIL_dev_package)

                Cursor.execute("SELECT" \
                        + " version, libname, libnamedbg, libnamedev" \
                        + " FROM `releases_dlpages_zl`" \
                        + " WHERE platform = '" + Distrib_name + "_" + Release_name + "'" \
                        + " AND arch = '" + Arch + "';")
                Result = Cursor.fetchone()
                if Result != None:
                    ZL_version = Result[0]
                    ZL_lib_name = Result[1]
                    ZL_lib_name_dbg = Result[2]
                    ZL_lib_name_dev = Result[3]
                    Content = Content.replace("ZL_VERSION", ZL_version)
                    Content = Content.replace("ZL_PACKAGE", ZL_lib_name)

                    if Project == "mi" \
                    and (Distrib_name + "_" + Release_name == "CentOS_4" \
                    or Distrib_name + "_" + Release_name == "RHEL_4" \
                    or Distrib_name + "_" + Release_name == "Debian_4.0") \
                    or Distrib_name == "Arch" :
                        ZL_dev_package = ""
                    else:
                        ZL_dev_package = " <small>(<a href=\"https://mediaarea.net/download/binary/libzen0/" + ZL_version + "/" + ZL_lib_name_dev + "\">devel</a>)</small>"
                    Content = Content.replace("ZL_DEV_PACKAGE", ZL_dev_package)

                if Release_with_wx == True:
                    Wx_package = Config[ Release_in_config_file + "_wx" ]
                    Wx_package = Wx_package.replace("DISTRIB_RELEASE", Distrib_name + "_" + Release_name)
                    Wx_package = Wx_package.replace("RELEASE_ARCH", Package_infos[Package_type][Arch])
                else:
                    Wx_package = ""
                Content = Content.replace("WX_PACKAGE", Wx_package)

                Destination.write(Content)

            # For the link to RHEL7 ppc64
            if Distrib_name + Release_name == "CentOS7":
                PPC_line = Config[ Project.upper() + "_" + Release_in_config_file + "_ppc64" ]
                Destination.write(PPC_line + "\n")

        if Project == "mi":
            Old_releases_path = Script_emplacement + "/dl_templates/MI_" + Distrib_name_lower + "_old_releases"
            if os.path.isfile(Old_releases_path):
                Old_releases_file = open(Old_releases_path, "r")
                Old_releases = Old_releases_file.read()
                Old_releases_file.close()

                # Debian 6 packages for Ubuntu 12.04
                if Distrib_name_lower == "ubuntu":
                    Request = "SELECT version" + " FROM " + Table_releases_dlpages \
                        + " WHERE platform = 'Debian_6.0'"
                    Cursor.execute(Request)
                    Result = Cursor.fetchone()
                    if Result != None:
                        MI_deb6_version = Result[0]
                    Old_releases = Old_releases.replace("MI_VERSION", MI_deb6_version)
                    Request = "SELECT version" + " FROM `releases_dlpages_zl`" \
                        + " WHERE platform = 'Debian_6.0'"
                    Cursor.execute(Request)
                    Result = Cursor.fetchone()
                    if Result != None:
                        ZL_deb6_version = Result[0]
                    Old_releases = Old_releases.replace("ZL_VERSION", ZL_deb6_version)

                Destination.write(Old_releases)

        Destination.write("</tbody>\n</table>\n")
        if Project == "mi":
            Destination.write("</body>\n</html>\n")
        Destination.close()

    # Close the access to the DB
    Cursor.close()

##################################################################
# Main

#
# Arguments
#
# 1 Project: mc, mi
# 2 OS name: windows, mac, linux
# For Windows and Mac: 3 MC|MI version and 4 MIL version

#
# Handle the variables
#

Project = sys.argv[1]
OS_name = sys.argv[2]
# The directory from where the python script is executed
Script_emplacement = os.path.dirname(os.path.realpath(__file__))

if Project != "mc" and Project != "mi":
    print
    print "The first argument must be mc or mi"
    print
    sys.exit(1)

if OS_name != "windows" and OS_name != "mac" \
and OS_name != "linux" and OS_name != "sources" \
and OS_name != "all":
    print
    print "The second argument must be windows, mac, linux, sources, or all"
    print
    sys.exit(1)

if OS_name == "windows" or OS_name == "mac" or OS_name == "all":
    # sys.argv[0] == Generate_DL_pages.py
    if len(sys.argv) < 6:
        print
        print "If you ask windows, mac, sources or all, you must provide the version"
        print "numbers of MC|MI + MIL, ZL respectively as 3rd, 4th and 5th arguments."
        print
        sys.exit(1)
    else:
        Project_version = sys.argv[3]
        MIL_version = sys.argv[4]
        ZL_version = sys.argv[5]

Config = {}
execfile( os.path.join( Script_emplacement, "Generate_DL_pages.conf"), Config)

HOR_config = {}
execfile( os.path.join( Script_emplacement, "Handle_OBS_results.conf"), HOR_config)

Package_infos = HOR_config["Package_infos"]

subprocess.call(["rm -fr /tmp/" + Project + "_dl_pages"], shell=True)
subprocess.call(["mkdir /tmp/" + Project + "_dl_pages"], shell=True)

if OS_name == "windows" or OS_name == "mac":
    DL_pages(OS_name)

if OS_name == "linux":
    OBS()

if OS_name == "sources":
    Sources()

if OS_name == "all":
    DL_pages("windows")
    DL_pages("mac")
    OBS()
    Sources()
