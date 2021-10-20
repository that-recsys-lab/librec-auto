============
Command Line
============

``librec-auto`` is designed to be run from the command line to enable unattended operation.

Here is an example command line 

::

    $ python -m librec_auto run -t study01 -c sample-config.xml -dr


The command line has both required and optional elements:

Required elements
===========

Command
-------

The command indicates what type of operation ``librec-auto`` will perform. This is the first element on the command line.

- ``run``: Run a complete librec-auto experiment. Re-uses cached results if any. May result in no action if all computations are up-to-date and no purge option is specified.
- ``split``: Run the training / test split operation only. 
-  ``exp``: Run the experiments, re-ranking, evaluation, and post-processing steps. (Assume training/test split already exists.)
- ``rerank``: Run the re-ranking, evaluation and post-processing steps. (Uses existing experimental results.) Same as ``eval`` if there is no re-ranking element in the configuration.
- ``eval``: Run the evaluation and post-processing steps. 
- ``post``: Run only post-processing step,
- ``purge``:Purge cached computations. Uses -p flag to determine what to purge
- ``status``: Print out the status of the experiments
- ``check``: Checks the configuration file and study for errors or problems. The check command is run by default when a study is run, but it can be run separately to check for problems in advance.

Target ``-t`` or ``--target``
------
A target is required. This is a path to a study directory where the experiments will be computed, temporary data will be stored, etc. By default, it is assumed that this directory will have a ``conf`` directory where the configuration information for the study will be found. This behavior can be overridden with the ``-c`` flag.

Optional elements
=============

Purge / No-purge
-----------

- ``-p`` or ``--purge`` Options: ``all``, ``split``, ``results``, ``rerank``, ``post``. Deletes results of the given steps and _all_ subsequent steps. Default is ``all``. The user is still prompted to confirm any purging.
- ``-q`` or ``--quiet`` If this flag is present, there will be no prompt and purging will happen automatically. 

Right now, the only way to not purge results is to say no to the prompt. 

Dry-run
----------

- ``-dr`` or ``--dry_run`` A dry-run walks through all of the steps of the configuration and indicates what actions would be performed, but none of the underlying computations are performed. For example, the command line that would be used to invoke a script is shown, but the script is not run. This can be useful for debugging and making sure that your configuration / command line is working as intended.

No-parallel
---------

- ``-np`` or ``--no_parallel`` The systems looks to the ``thread-count`` element in the configuration file to determine whether or not to run parallelizable operations on separate threads. If this flag is set, this elements is ignored and all operations are run sequentially.

Passwords
-------

- ``-k`` or ``--key_password`` If a password is supplied here, it will be used to decrypt the key file needed to access API keys for post-processing operations, such as Slack or Dropbox posting of results. Such a file must have been created using the ``encrypt.py`` utility.

No check
--------

- ``-nc`` or ``--no_check`` If this flag is specified, configuration file checking will be skipped. Use at your own risk! 

