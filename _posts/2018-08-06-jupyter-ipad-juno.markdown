---
layout: post
title:  "Using Juno app on iPad to run Jupyter notebooks."
description: "How to run Jupyter notebooks on iPad using the Juno app."
date:   2018-08-12 06:07:00 +0100
categories: 
---
## Introduction

This post will describe the steps to follow in order to run Jupyter notebooks on a remote server from an iPad Pro.

We'll use [Juno app][juno_app] on the iPad to run Jupyter notebooks hosted on a [Digital Ocean][digital-ocean] server.

## Create Digital Ocean server

To setup the server, follow the steps below:

* Create a Digital Ocean account using my [referral][referral-code] code.  You get $10 credit (approx. two months of usage)
* [Create][ssl-key] an SSL key on your local machine, in order to use SSL to log on to the server.
* [Add][add-key] the SSL key to your Digital Ocean account
* [Follow][digitalocean-quick] the Digital Ocean quick start guide to set up your server.
* Log on to the server using SSL, for example:

    ``` bash
    ssh root@123.45.678.901
    ```

## Install and configure Jupyter notebooks

You'll need to use SSH in order to connect from the Juno app to the server.

1. Firsly follow [these][juno-ssh] steps in order to generate the certificates and keys.
2. Take note of the three keys/certificates that are produced.  You’ll need these in the next step.
3. Clone [this][do-repository] repository to your local machine (not your server).
4. Copy the two certificates from the first step into the same directory.
5. Execute the setup_server.sh file, which installs anaconda and the associated machine learning libraries and sets up the Jupyter notebook.

	``` bash
    bash setup_server.sh THE-IP-ADDRESS
	```
6. Restart the server
7. Now run the notebook in a Screen session (this means that it will run in a background process.
	
	``` bash
	screen 
    jupyter notebooks --allow-root
	```
8. To detach from Screen `ctrl-a-d`

Jupyter is now running on your Digital Ocean server.  The final step is to connect to it from the Juno app on the iPad.  Remember to follow all the instructions in step 1. above, especially emailing the certificate to yourself (so that you can install on the iPad).


[referral-code]:https://m.do.co/c/399038ff7529
[add-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/
[do-repository]:https://github.com/ioancw/Digital-Ocean-Droplet-Creation
[ssl-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/create-with-openssh/
[digitalocean-quick]: https://www.digitalocean.com/docs/droplets/quickstart/
[juno_app]: https://juno.sh
[digital-ocean]: https://www.digitalocean.com
[juno-ssh]: https://juno.sh/ssl-self-signed-cert/
