#!/bin/bash
aws s3 cp --recursive  model  s3://shibacow-misc-backup/model/
aws s3 cp --recursive  log  s3://shibacow-misc-backup/log/
