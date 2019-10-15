#!/bin/bash

TMP_DIR=$(mktemp -d)
PROD_ZIP_NAME=prod
PROD_FOLDER=prod
PROD_LAMBDA_NAME=boba-backend-gateway
PROD_ZIP_PATH=$TMP_DIR/$PROD_ZIP_NAME.zip
TEST_ZIP_NAME=test
TEST_FOLDER=test
TEST_LAMBDA_NAME=boba-backend-gateway-test
TEST_ZIP_PATH=$TMP_DIR/$TEST_ZIP_NAME.zip

PROJ_DIR="$(dirname "$0")"

if [ -z "$1" ];  then
    echo "Must supply argument \"prod\" or \"test\"."
elif [ $1 = "prod" ]; then
    cd $PROJ_DIR/$PROD_FOLDER
    zip -r9 $PROD_ZIP_PATH .
    aws lambda update-function-code --function-name $PROD_LAMBDA_NAME --zip-file fileb://$PROD_ZIP_PATH
elif [ $1 = "test" ]; then
    cd $PROJ_DIR/$TEST_FOLDER
    zip -r9 $TEST_ZIP_PATH .
    aws lambda update-function-code --function-name $TEST_LAMBDA_NAME --zip-file fileb://$TEST_ZIP_PATH
else
    echo "Invalid argument. Must supply argument \"prod\" or \"test\"."
fi

rm -rf $TMP_DIR
