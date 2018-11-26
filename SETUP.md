# Setup 

## Manual Setup

### macOS Setup

Find by text on iOS Simulator is based on macOS Accessibility.
In order to get tests working you should allow program that execute tests to be able to control your computer.
```
System Preferences -> Security & Privacy ->  Privacy -> Accessibility -> 
- Add Terminal to list of apps allowed to control your computer (to be able to run tests via Terminal)
- Add PyCharm to list of apps allowed to control your computer (to be able to run tests via IDE)
```

## Environment Variables 
In order to run tests some environment variables should be set.

### Building Android and iOS apps

Android release builds require:
      
    ANDROID_KEYSTORE_PATH - Path to the keystore file
    
    ANDROID_KEYSTORE_PASS - Password for the keystore file
    
    ANDROID_KEYSTORE_ALIAS
    
    ANDROID_KEYSTORE_ALIAS_PASS
    
iOS release builds for device require:

    DEVELOPMENT_TEAM - Development team
    
    PROVISIONING - Development provisioning profile
    
    DISTRIBUTION_PROVISIONING - Distribution provisioning profile

### Other

Git settings (optional)

    SSH_CLONE - True or False (if not set tests will default to False).

Skip `tns doctor` (optional)
 
    NS_SKIP_ENV_CHECK - If set (no matter of the value) doctor is not executed.