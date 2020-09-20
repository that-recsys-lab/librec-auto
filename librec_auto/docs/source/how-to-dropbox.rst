.. _DropboxIntegration:

===================
Dropbox Integration
===================
:Author:
		Robin Burke, Zijun Liu
:Version:
		June 5th, 2020

1. Introduction
===============

Dropbox Integration is based on the Dropbox API, and enables users to post files and folders to Dropbox locations. The Dropbox API key is password-encrypted and the encrypted key can be included in a public repository (i.e. GitHub). 

2. Installation
===============

2.0. QuickStart Guide
---------------------

	pip install dropbox

2.1. Go to Dropbox Official Website
-----------------------------------

1. Go to website. https://www.dropbox.com/developers

2. Click **Create apps** on the page. See Figure1 below.

.. figure:: images/dropbox-integration/1.png
   :align: center
   :width: 600
   :alt: Management Tools

   *Figure1*

2.2. Create new app on Dropbox 
------------------------------

1. **Choose an API**. There are two types of Dropbox API. *Dropbox API* and *Dropbox Business API*. For personal, you can choose **Dropbox API**.

2. **Choose the type of access you need**. There are two types of access too. *App folder* means you can upload your files on selected folder. This is recommended as it provides additional security for your Dropbox folder.

3. **Name your app**. Give a name for your Dropbox API app name. i.e. *test2*. See Figure2 below.

.. figure:: images/dropbox-integration/2.png
   :align: center
   :width: 600
   :alt: Management Tools

   *Figure2*

2.3. Save your Dropbox API key
------------------------------

1. After you finish section 2.2. Click the *Continue* button below. You have successfully created your Dropbox API app. 

2. See Figure3 below. Figure3 is the **OAuth 2** section. The **Generated access token** is space for your Dropbox API. Copy the API key to a text file. Do not store this file in your study directory with data files, etc. that you might want to share with others on GitHub, for example.

.. figure:: images/dropbox-integration/3.png
   :align: center
   :width: 600
   :alt: Management Tools

   *Figure3*
   

3. Integrating with librec-auto
===============================

3.1. Encrypt your Dropbox API key
----------------------------------------

1. As above, your secret key should be stored in a secure location.

2. To encrypt the key to create a file that can be shared securely, run the script ``bin/encrypt.py``. Include the following arguments:

* ``--encrypted`` This is the file that contains the API key in encrypted form. This will typically be placed in your study directory in a directory called ``keys``. 
* ``--key`` This is the cleartext API key that you got from Slack.

The call will look like this:

``python bin/encrypt.py --encrypted mystudy/keys/dropbox-api.enc --key non-shared-safe-location/dropbox-api.key``

3. The script will prompt you for a password. You will need this password later to use the encrypted API key.


3.2. Add the script to the configuration file
---------------------------------------------

1. In order to add Dropbox integration to your study, you will need to add a ``script`` element to the post-processing portion of the configuration file. Here is an example:

::

   <script lang="python3" src="system">
   	<script-name>dropbox-post.py</script-name>
   	<param name="option">file</param>
   	<param name="encrypted_key">keys/dropbox-api.enc</param>
   	<param name="path">post/cool-graphic.jpg</param>
   	<param name="dest">/app-folder-on-dropbox</param>
   	<param name="password"/>
   </script>
 
The parameters are as follows:

* ``option`` Either ``file`` or ``folder``. The above example is a ``file`` example. 
* ``channel`` The Slack channel where the message should be posted. Do not include the hashtag. 
* ``encrypted_key`` The location of the encrypted API key. This is relative to the study directory where the configuration is located.
* ``path`` The file/folder that will be posted in the designated folder when the script is executed.
* ``dest`` The destination folder on Dropbox where files will be sent.
* ``password`` Do not include the password here. (You'll notice that the element has no content.) This is a flag indicating that the password will be entered on the command line when ``librec-auto`` is run. If you do not include it, you will be prompted for the password when the script is run, but that kind of defeats the purpose of having an automated experimental tool.

To post the contents of a folder to Dropbox, the ``option`` element will contain the term ``folder`` instead of ``file``. The ``path`` argument will then be interpreted as the path to a folder.

3.3. Provide the password when running librec-auto

Use the ``-k`` or ``--key_password`` on the command line to provide the password to librec-auto. Example:

``python -m librec_auto -k my_password_here run``

The password can be shared with collaborators via some secure channel. The same password will be used for all scripts containing the empty ``<password/>`` element.
