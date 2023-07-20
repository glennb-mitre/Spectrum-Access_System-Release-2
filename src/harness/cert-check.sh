#!/bin/bash

# if no argument was given at runtime.
if [ $# -eq 0 ] 
then
  echo "Enter the path to your SAS cert directory?"
  read dirpath

  # File Operations.
  if [ -f $dirpath ] 
  then
    printf "\nA file was provided\n\n"

    if [[ $(file -b "$dirpath") == "PEM certificate" ]]; 
    then
      echo "A certificate file was given"
    else
      echo "No certificate file was given"
    fi 
  fi
 

  # Directory Operations.
  if [ -d $dirpath ] 
  then
    printf "\nA directory was provided\n"

    declare -a dircerts
    declare -a expcerts
    declare -a cacerts
    declare -a cadir

    
    printf "\nNon certificate files in directory:\n"
    # Find certs in directory.
    for dircontent in "$dirpath"/*
    do
      dircontent=$(basename "$dircontent")
      if [[ $(file -b "$dircontent") == "PEM certificate" ]];
      then
        dircerts+=( $dircontent )
      else
        echo $dircontent
      fi    
    done

    # Check for expired certs.
    for index in ${!dircerts[@]}
    do
      if !(openssl x509 -checkend 86400 -noout -in ${dircerts[$index]} 1>/dev/null)
      then
        expcerts+=( ${dircerts[$index]} )
      fi
    done

    printf "\nExpired Certs:\n"
    if [ expcerts == 0 ]
    then 
      echo "There are no expired certs in the directory"
    else
      for expcert in ${expcerts[@]}
      do
        echo ${expcert}
      done
    fi

    # Check if CA cert is in the system certificate store.
    printf "\nCerts in the system keychain:\n"

    # Get an array of the default ca directory filenames.
    for cadir in "/etc/ssl/certs"/*
    do
      cadirfile=$(basename "$cadir")
      cadirfiles+=( $cadirfile )

      if [[ ${dircerts[*]} =~ $cadirfile ]]
      then
        printf "${cadirfile}\n"
      fi
    done

    # Check if any local certs are in the system ca store.
    printf "\nCerts not in system keychain:\n"
    for dircert in ${dircerts[@]}
    do 
      if [[ ${cadirfiles[*]} =~ $dircert ]]
      then
        cacerts+=( $dircert )
        echo "***************IN FUNCTION******************* ${dircert}"
      else
        echo $dircert
      fi
    done

  fi

# If arguments were given at runtime.
else
  
  # If more than 1 argument was given.
  if [ $# -ge 2 ] 
  then
    echo Multiple arguments entered

  # Help menu.
  else [ $1 = -h ] || [ $1 = --help ] 
    echo "Usage: cert-check.sh [FILE] [DIR]"
    echo "Validate the given certificate(s) or directory of certificates."
    echo ""
    echo "Options:"
    echo "-d, --directory      Check for valid certs in the given directory"
    echo "-f, --file           Check if the given file is a valid certificate"
    echo "-h, --help           Display this help dialog"
  fi   
fi




