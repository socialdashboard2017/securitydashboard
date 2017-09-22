import os

class BaseConfig(object):
  DEBUG = False
  SECRET_KEY = '\xadl\xdbip\xf6\xef\xf2\\\x16c\x9c\xdbW\xc8\x8c@\xc1H\xda\x16\xe0\x1b\xe6'
  # str(os.urandom(24))
  # SQLALCHEMY_DATABASE_URI = 'postgres://nclidqssuyrhop:15a3934af0709ebcc2f2323ffe3bc91b775cb01b5a50c96d43bec66ac5da4b56@ec2-54-247-81-76.eu-west-1.compute.amazonaws.com:5432/d4nu80t6oqurdq'
  SQLALCHEMY_DATABASE_URI = 'postgres://ebjvvrvufogrrq:8c10272613e7515d73c722d3938a9e37188af2b33c21bebf9addd2e599475c34@ec2-79-125-125-97.eu-west-1.compute.amazonaws.com:5432/ddsjbk4k0ulhnc'
  #'postgres://nclidqssuyrhop:15a3934af0709ebcc2f2323ffe3bc91b775cb01b5a50c96d43bec66ac5da4b56@ec2-54-247-81-76.eu-west-1.compute.amazonaws.com:5432/d4nu80t6oqurdq'
  #'postgres://xppbgyavrujprb:d2dbd2253a86096dc28c78bd9d5d273f0ea5c4e188fe7041d3446c65e88c2caf@ec2-54-217-222-254.eu-west-1.compute.amazonaws.com:5432/df9v7lmbj9r8r5'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
