# Test Settings
In order to run tests some environment variables should be set.

## Building Android and iOS apps

Android release builds require:
      
    ANDROID_KEYSTORE_PATH - Path to the keystore file
    
    ANDROID_KEYSTORE_PASS - Password for the keystore file
    
    ANDROID_KEYSTORE_ALIAS
    
    ANDROID_KEYSTORE_ALIAS_PASS
    
iOS release builds for device require:

    DEVELOPMENT_TEAM - Development team
    
    PROVISIONING - Development provisioning profile
    
    DISTRIBUTION_PROVISIONING - Distribution provisioning profile

## Update Apps

### Short-hand environment properties

You can set `TEST_ENV` to
```
export TEST_ENV=next/rc/something-else-means-LIVE-env
```
It is translated to:
```
class EnvironmentType(Enum):
    _init_ = 'value string'

    NEXT = 1, 'next'
    RC = 2, 'rc'
    LIVE = 3, 'latest'

    def __str__(self):
        return self.string
```
Some tests use this logic and do not update apps when 
`Settings.ENV == EnvironmentType.LIVE`


## Other Settings

Git settings (optional)

    SSH_CLONE - True or False (if not set tests will default to False).

Skip `tns doctor` (optional)
 
    NS_SKIP_ENV_CHECK - If set (no matter of the value) doctor is not executed.