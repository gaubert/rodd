#!/bin/bash
# version 0.5
#set -x

### ./uncompress dir-to-uncompress (Uncompress all sub-dirs below that)



targetdir="$1"
origdir=`pwd`

# look for zip files

echo "========================== Unzip process =========================="

files=`find $1 -name *.zip -o -name *.ZIP`

for file in $files
do
    #get abs path
    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
    dir=`dirname $abs_file`
    cd $dir

    # Create unzip directory
    zip_dir=$dir/$(basename ${abs_file} .zip)
    if [ ! -d ${zip_dir} ]
    then
      if ! mkdir ${zip_dir}
      then
         echo "$0 - Failed to create directory : ${zip_dir}"
         return 1
      fi
    fi
    echo "unzip $abs_file"

    # Unzip in unzip directory
    if ! unzip -o ${abs_file} -d ${zip_dir}
    then
      echo "$0 - Unzip error for file : ${abs_file}"
      return 1
    else
      echo "Delete file ${abs_file}"
      rm -f ${abs_file}
    fi

    #go back to original
    cd $origdir
done

echo "========================== tar.bz2 process =========================="

# look for tar.bz2 files
files=`find $1 -name *.tar.bz2 -o -name *.tbz2 -o -name *.TAR.BZ2 -o -name *.tar.bz2`

for file in $files
do
    #get abs path
    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
    dir=`dirname $abs_file`
    cd $dir

    echo "bunzip2 $abs_file"

    # bunzip  file
    if ! tar jxvf ${abs_file}
    then
      echo "$0 - tar error for file : ${abs_file}"
      return 1
    else
      echo "Delete file ${abs_file}"
      rm -f ${abs_file}
    fi

    #go back to original
    cd $origdir
done

echo "========================== bz2 process =========================="

# look for bz2 files
files=`find $1 -name *.bz2 -o -name *.BZ2`

for file in $files
do
    #get abs path
    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
    dir=`dirname $abs_file`
    cd $dir

    echo "bunzip2 $abs_file"

    # bunzip  file 
    if ! bunzip2 -f ${abs_file} 
    then
      echo "$0 - bunzip2 error for file : ${abs_file}"
      exit 1
    fi

    #go back to original
    cd $origdir
done

echo "========================== tar.gz process =========================="

# look for tar.gz files
files=`find $1 -name *.tar.gz -o -name *.tgz -o -name *.TAR.GZ -o -name *.TGZ`

for file in $files
do
    #get abs path
    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
    dir=`dirname $abs_file`
    cd $dir

    echo "untar $abs_file"

    # bunzip  file
    if ! tar zxvf ${abs_file}
    then
      echo "$0 - tar error for file : ${abs_file}"
      exit 1
    else
      echo "Delete file ${abs_file}"
      rm -f ${abs_file}
    fi

    #go back to original
    cd $origdir
done

echo "========================== gz process =========================="

# look for gz files
files=`find $1 -name *.gz -o -name *.GZ`

for file in $files
do
    #get abs path
    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
    dir=`dirname $abs_file`
    cd $dir

    echo "gunzip $abs_file"

    # gunzip  file 
    if ! gunzip ${abs_file} 
    then
      echo "$0 - gunzip error for file : ${abs_file}"
      exit 1
    fi

    #go back to original
    cd $origdir
done

#echo "========================== tar process =========================="

# look for tar files
#files=`find ./test-dir -name *.tar -o -name *.TAR`

#for file in $files
#do
    #get abs path
#    abs_file="$( readlink -f "$( dirname "$file" )" )/$( basename "$file" )"

    #get abs dir and go in it
#    dir=`dirname $abs_file`
#    cd $dir

#    echo "p $abs_file"

    # tar  file
#    if ! tar zxvf ${abs_file}
#    then
#      echo "$0 - tar error for file : ${abs_file}"
#      exit 1
#    else
#      echo "Delete file ${abs_file}"
#      rm -f ${abs_file}
#    fi

    #go back to original
#    cd $origdir
#done
