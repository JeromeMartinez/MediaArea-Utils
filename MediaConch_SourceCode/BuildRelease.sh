# MediaConch_SourceCode/Release/BuildRelease.sh
# Build a release of MediaConch

# Copyright (c) MediaArea.net SARL. All Rights Reserved.
# Use of this source code is governed by a BSD-style license that
# can be found in the License.html file in the root of the source
# tree.

function _build_mac () {

    local sp RWDir

    # SSH prefix
    sp="ssh -p $SSHPort $SSHUser@$IP"
    RWDir="/Users/mymac/Documents/almin"

    # Clean up
    $sp "cd $RWDir/ ;
            rm -fr build ;
            mkdir build"

    echo
    echo "Compile Mac MC CLI..."
    echo

    scp -P $SSHPort archives/MediaConch_CLI_${Version_new}_GNU_FromSource.tar.xz $SSHUser@$IP:$RWDir/build
            #cd MediaConch_CLI_${Version_new}_GNU_FromSource ;
    $sp "cd $RWDir/build ;
            tar xJf MediaConch_CLI_${Version_new}_GNU_FromSource.tar.xz ;
            cd MediaConch_CLI_GNU_FromSource ;
            cp -r ../../libxml2 . ;
            ./CLI_Compile.sh"

    echo
    echo "Compile Mac MC GUI..."
    echo

    scp -P $SSHPort archives/MediaConch_GUI_${Version_new}_GNU_FromSource.tar.xz $SSHUser@$IP:$RWDir/build
            #cd MediaConch_GUI_${Version_new}_GNU_FromSource ;
    $sp "cd $RWDir/build ;
            tar xJf MediaConch_GUI_${Version_new}_GNU_FromSource.tar.xz ;
            cd MediaConch_GUI_GNU_FromSource ;
            cp -r ../../libxml2 . ;
            PATH=$PATH:~/Qt/5.3/clang_64/bin ./GUI_Compile.sh"

    echo
    echo "Making and fetching back the dmg..."
    echo

            #cd MediaConch_CLI_${Version_new}_GNU_FromSource ;
            #cd MediaConch_GUI_${Version_new}_GNU_FromSource ;
    $sp "cd $RWDir/build ;
            $KeyChain ;
            cd MediaConch_CLI_GNU_FromSource/MediaConch/Project/Mac ;
            ./mkdmg.sh mc cli $Version_new ;
            cd - > /dev/null ;
            cd MediaConch_GUI_GNU_FromSource/MediaConch/Project/Mac ;
            PATH=$PATH:~/Qt/5.3/clang_64/bin ./mkdmg.sh mc gui $Version_new"

    mkdir mac
    scp -P $SSHPort "$SSHUser@$IP:$RWDir/build/MediaConch_CLI_GNU_FromSource/MediaConch/Project/Mac/MediaConch_CLI_${Version_new}_Mac.dmg" mac
    scp -P $SSHPort "$SSHUser@$IP:$RWDir/build/MediaConch_GUI_GNU_FromSource/MediaConch/Project/Mac/MediaConch_GUI_${Version_new}_Mac.dmg" mac

}

function btask.BuildRelease.run () {

    # TODO: incrementals snapshots if multiple execution in the
    # same day eg. AAAAMMJJ-X
    #if b.path.dir? $WDir/`date +%Y%m%d`; then
    #    mv $WDir/`date +%Y%m%d` $WDir/`date +%Y%m%d`-1
    #    WDir=$WDir/`date +%Y%m%d`-2
    #    mkdir -p $WDir
    # + handle a third run, etc
        
    WDir="$WDir/`date +%Y%m%d`/mc"
    rm -fr $WDir
    mkdir -p $WDir
    cd $WDir

    echo
    echo Clean up...
    echo

    rm -fr upgrade_version
    rm -fr prepare_source
    rm -fr archives
    rm -fr mac

    mkdir upgrade_version
    mkdir prepare_source

    cd $(b.get bang.working_dir)/../upgrade_version
    $(b.get bang.src_path)/bang run UpgradeVersion.sh -p mc -o $Version_old -n $Version_new -w "$WDir/upgrade_version"

    cd $(b.get bang.working_dir)/../prepare_source
    #$(b.get bang.src_path)/bang run PrepareSource.sh -p mc -v $Version_new -all -s "$WDir/upgrade_version/MediaConch_SourceCode" -w "$WDir/prepare_source"
    $(b.get bang.src_path)/bang run PrepareSource.sh -p mc -v $Version_new -all -s "$WDir/upgrade_version/MediaConch_SourceCode" -w "$WDir/prepare_source" -nc

    cd $WDir
    mv prepare_source/archives .

    if [ "$Target" = "mac" ]; then
        _build_mac
    fi
    if [ "$Target" = "windows" ]; then
        echo _build_windows
    fi
    if [ "$Target" = "linux" ]; then
        echo _build_linux
    fi
    if [ "$Target" = "all" ]; then
        _build_mac
        echo _build_windows
        echo _build_linux
    fi

    if $CleanUp; then
        cd $WDir
        rm -fr upgrade_version
        rm -fr prepare_source
    fi

}