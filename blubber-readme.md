Wikispeech-server SOX proxy will spin up on port 5000.

In addition to the standard `?lang=en&input=test` parameters,
it will also accept `&speechoidUrl=` which will override the environment variable.

## Environment variables

| Name                            | Default value                     | Description                                                       |
| ------------------------------- |:---------------------------------:| ----------------------------------------------------------------- |
| SPEECHOID_URL                   | http://wikispeech-server:10001/   | The Speechoid URL to act proxy against                            |
