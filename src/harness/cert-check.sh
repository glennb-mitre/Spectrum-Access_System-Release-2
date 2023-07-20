#!/bin/bash

# if no argument was given at runtime.
if [ $# -eq 0 ] 
then
  echo "Enter the path to your SAS cert directory?"
  read dirpath

  # File Operations.
  if [ -f $dirpath ] 
  then
    echo "A file was given"

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
    echo A directory was given
    declare -a dircerts
    declare -a expcerts

    # Find certs in directory.
    for dircontent in "$dirpath"/*
    do
      if [[ $(file -b "$dircontent") == "PEM certificate" ]];
      then
        dircerts+=( $dircontent )
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

    if [ expcerts == 0 ]
    then 
      echo "There are no expired certs in the directory"
    else
      echo "Expired Certs:"
      for expcert in ${expcerts[@]}
      do
        echo ${expcert}
      done
    fi
  fi

# If arguments were given at runtime.
else
  
  # If more than 1 argument was given.
  if [ $# -ge 2 ] 
  then
    echo Multiple arguments entered

  # Help Menu.
  else [ $1 = -h ] || [ $1 = --help ] 
    echo "Usage: cert-check.sh [FILE] [DIR]"
    echo "Validate the given certificate(s) or directory of certificates."
    echo ""
    echo "Options:"
    echo "-d, --directory      Check for valid certs in the given directory"
    echo "-f, --file           Check if the given file is a valid certificate"
    echo "-h, --help           Display this help dialog"
    echo ""
    echo "File Options:"
    echo "-c, --ca"
    echo ""
    echo "Directory Options:"
    echo "-v, --invert           Inverts match from certs to non-certs"
  fi   
fi




