---
layout: post
title:  "Juno app on iPad."
date:   2018-08-06 21:29:25 +0100
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

* Firsly follow [these][juno-ssh] steps in order to generate the certificates and keys.
* Now take the following files from my repository.


[referral-code]:https://m.do.co/c/399038ff7529
[add-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/to-account/
[ssl-key]:https://www.digitalocean.com/docs/droplets/how-to/add-ssh-keys/create-with-openssh/
[digitalocean-quick]: https://www.digitalocean.com/docs/droplets/quickstart/
[juno_app]: https://juno.sh
[digital-ocean]: https://www.digitalocean.com
[juno-ssh]: https://juno.sh/ssl-self-signed-cert/
