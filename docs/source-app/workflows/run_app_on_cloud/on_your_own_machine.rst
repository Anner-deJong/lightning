#######################
Run on your own machine
#######################

**Audience:** Users who want to run Lightning App on a remote machine.

----

***********
Run via ssh
***********
To run a Lightning App on any machine, simply ssh to the machine and run the app directly

.. code:: bash

    # log into your cloud machine
    ssh your_name@your_cloud_machine

    # get your code on the machine and install deps
    ...

    # start the app
    lightning run app app.py
