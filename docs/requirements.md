# General requirements for smooth running of the ASF-Tools
## Configuration
The ASF-Tools `api/clarity` submodules establish a connection to the Clarity API to provide the user with relevant information. For successful execution, either a configuration file must be located in the user's home directory, or its path must be explicitly specified during initialization.

To define the configuration file’s path explicitly, use:
`ClarityLimsMock(credentials_path="your/path/to/config")`
By default, the system will look for a file named .clarityrc in the home directory.

The configuration file should be formatted as follows:

````
[clarity]
baseuri = "https://asf-claritylims.thecrick.org/"
username = "user"
password = "password"
````

The `username` and `password` values should match the credentials used to access each user's Clarity account or to generate a `.genologics` config file.
