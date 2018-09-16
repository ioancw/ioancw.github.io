---
layout: post
title:  "Running Jupyter notebook on iPad using Juno app."
description: "How to run Jupyter notebooks on iPad using the Juno app."
date:   2018-08-11 06:07:00 +0100
categories: 
---
## Introduction

Since getting an iPad Pro last year, I've been looking at ways of using it to run Jupyter notebooks. One option is to run Jupyter notebooks on a remote server and then connecting via Safari.  While this method works, using Safari for this is clunky on the iPad.

I started searching for a dedicated app, until I found [Juno app][juno_app], after which there was no point looking further.

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
2. Take note of the three keys/certificates that are produced.  You’ll need these in the next steps.
    * `ca/certs/ca.cert.pem` is to be email to yourself, so you can use from the iPad.
    * `jupyter/certs/ssl.cert.pem` and `jupyter/private/ssl.key.pem` will be used below.
3. Clone [this][do-repository] repository to your local machine (not your server).
4. Copy `jupyter/certs/ssl.cert.pem` and `jupyter/private/ssl.key.pem` into the same directory as the clone of the repository.
5. Execute the setup_server.sh file, which installs Anaconda and the associated machine learning libraries and sets up the Jupyter notebook configuration file, then copies the key and certificate to the server.

	``` bash
    bash setup_server.sh 123.45.678.901
	```
6. Restart the server
7. Log on to your server and run the Jupyter notebook in a `Screen` session (this will allow the notebook to run in background process, and so won't be killed when you log out from the server).
	
	``` bash
	screen 
    jupyter notebooks --allow-root
	```
8. To detach from Screen `ctrl-a-d`.  It's now safe to log out from the server.

Jupyter is now running on your Digital Ocean server.  The final step is to connect to it from the Juno app on the iPad.  Remember to follow all the instructions in step 1. above, especially emailing the `ca/certs/ca.cert.pem` certificate to yourself (so that you can install on the iPad).

Here is an image of an example Jupyter workbook from within Juno.
![test-img]({{"/assets/img/math-jax-jekyll/IMG_0082.jpg" | absolute_url }})

[referral-code]:https://m.do.co/c/399038ff7529
[add-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/
[do-repository]:https://github.com/ioancw/Digital-Ocean-Droplet-Creation
[ssl-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/create-with-openssh/
[digitalocean-quick]: https://www.digitalocean.com/docs/droplets/quickstart/
[juno_app]: https://juno.sh
[digital-ocean]: https://www.digitalocean.com
[juno-ssh]: https://juno.sh/ssl-self-signed-cert/
