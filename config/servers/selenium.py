import copy


def get_default_job(job_name, browser, priority, template_file):
    """
    Default job dictionary, for all jobs in this Jenkins type.
    """
    default_job = {
        "job_name" : job_name,
        "template_file" : template_file,
        "max_builds_to_keep" : "30",
        "repo" : "git@github.com:<put your repo here>",
        "priority" : priority,
        "disabled" : False,
        "poll_scm" : False,
        "build_periodically" : "",
        "build_triggers" : "",
        "email_results": False,
        "testng_parallel" : True,
        "uses_plugin" : False,
        "suite" : ""
    }
    if browser in "chrome":
        default_job["slb"]="googlechrome"
        default_job["slbv"]=""
        default_job["slos"]="Windows 2003"
        default_job["waitTime"]="120"

    elif browser in "firefox.latest":
        default_job["slb"]="firefox"
        default_job["slbv"]="9."
        default_job["slos"]="Windows 2008"
        default_job["waitTime"]="120"

    elif browser in "firefox.3.6":
        default_job["slb"]="firefox"
        default_job["slbv"]="3.6."
        default_job["slos"]="Windows 2003"
        default_job["waitTime"]="120"

    elif browser in "ie.8":
        default_job["slb"]="iexplore"
        default_job["slbv"]="8."
        default_job["slos"]="Windows 2003"
        default_job["waitTime"]="240"

    elif browser in "ie.9":
        default_job["slb"]="iexplore"
        default_job["slbv"]="9."
        default_job["slos"]="Windows 2008"
        default_job["waitTime"]="240"

    elif browser in "safari.5":
        default_job["slb"]="safari"
        default_job["slbv"]="5"
        default_job["slos"]="Mac 10.6"
        default_job["waitTime"]="120"


    return copy.deepcopy(default_job)


def get_setup_job(browser, priority):
    """
    Job to build the web application under test.
    """
    jd = get_default_job("myrepo.build", browser, priority, "selenium-setup.xml")
    jd["build_triggers"]="core"+".chrome,"+\
                         "apps"+".chrome,"+\
                         "plugin.apps"+".chrome,"+\
                         "core"+".firefox.latest,"+\
                         "apps"+".firefox.latest,"+\
                         "plugin.apps"+".firefox.latest,"+\
                         "core"+".ie.8,"+\
                         "apps"+".ie.8,"+\
                         "plugin.apps"+".ie.8,"+\
                         "core"+".firefox.3.6,"+\
                         "apps"+".firefox.3.6,"+\
                         "plugin.apps"+".firefox.3.6,"+\
                         "core"+".ie.9,"+\
                         "apps"+".ie.9,"+\
                         "plugin.apps"+".ie.9,"+\
                         "core"+".safari.5,"+\
                         "apps"+".safari.5,"+\
                         "plugin.apps"+".safari.5"


    jd["poll_scm"]=True

    return jd


def get_test_job(job_name, browser, priority):
    """
    Standard test job.
    """
    return get_default_job(job_name, browser, priority, "selenium-suite.xml")


def get_test_core_job(browser, priority):
    """
    Core test job.
    """
    jd = get_test_job("core."+browser, browser, priority)
    jd["suite"]="app.functional,ad,admin.all,end.user,system"
    return jd

def get_test_active_apps_job(browser, priority):
    """
    Active apps test job.
    """
    jd = get_test_job("apps."+browser, browser, priority)
    jd["suite"]="active.app.login"
    return jd

def get_test_active_plugin_apps_job(browser, priority):
    """
    Active plugin apps test job.
    """
    jd = get_test_job("plugin.apps."+browser, browser, priority)
    jd["suite"]="active.plugin.app.login"
    jd["uses_plugin"]=True
    return jd

def get_test_new_apps_job(browser, priority):
    """
    New apps test job.
    """
    jd = get_test_job("new.apps."+browser, browser, priority)
    jd["suite"]="new.apps.test"
    jd["uses_plugin"]=True
    return jd

def get_test_plugin_detection_job(browser, priority):
    """
    Plugin detection test job.
    """
    jd = get_test_job("plugin.detection."+browser, browser, priority)
    jd["suite"]="plugin.app.bulk"
    jd["uses_plugin"]=True
    return jd

def get_test_serial_job(browser, priority):
    """
    Serial test job.
    """
    jd = get_test_job("serial."+browser, browser, priority)
    jd["suite"]="plugin.platform,user.management,exclude.from.parallel.run"
    jd["uses_plugin"]=True
    jd["testng_parallel"]=False
    return jd


def integration_jobs():
    """
    Full integration test job set.
    """
    jobs = []

    jobs.append(get_setup_job("chrome", 0))

    jobs.append(get_test_core_job("chrome", 1))
    jobs.append(get_test_active_apps_job("chrome", 2))
    jobs.append(get_test_active_plugin_apps_job("chrome", 3))

    jobs.append(get_test_core_job("firefox.latest", 4))
    jobs.append(get_test_active_apps_job("firefox.latest", 5))
    jobs.append(get_test_active_plugin_apps_job("firefox.latest", 6))

    jobs.append(get_test_core_job("ie.8", 7))
    jobs.append(get_test_active_apps_job("ie.8", 8))
    jobs.append(get_test_active_plugin_apps_job("ie.8", 9))

    jobs.append(get_test_core_job("firefox.3.6", 10))
    jobs.append(get_test_active_apps_job("firefox.3.6", 11))
    jobs.append(get_test_active_plugin_apps_job("firefox.3.6", 12))

    jobs.append(get_test_core_job("ie.9", 13))
    jobs.append(get_test_active_apps_job("ie.9", 14))
    jobs.append(get_test_active_plugin_apps_job("ie.9", 15))

    return jobs


def pre_integration_jobs():
    """
    Subset of full integration test job set.
    """
    jobs = []

    t = get_setup_job("firefox.latest", 10)
    t["build_triggers"]="core.firefox.latest"
    jobs.append(t)
    jobs.append(get_test_core_job("firefox.latest", 9))
    t = get_setup_job("firefox.latest", 8)
    t["build_periodically"]="0 16 * * *"
    t["build_triggers"]="new.apps.firefox.3.6,"+\
                        "new.apps.firefox.latest,"+\
                        "new.apps.ie.8,"+\
                        "new.apps.ie.9,"+\
                        "plugin.detection.firefox.latest"
    t["repo"]="git@github.com:<put a different fork of your repo here>"
    jobs.append(t)
    jobs.append(get_test_new_apps_job("firefox.3.6", 7))
    t=get_test_new_apps_job("ie.8", 6)
    t["uses_plugin"]=True
    jobs.append(t)
    t=get_test_new_apps_job("ie.9", 5)
    t["uses_plugin"]=True
    jobs.append(t)
    jobs.append(get_test_plugin_detection_job("firefox.latest", 4))

    return jobs


def serial_jobs():
    """
    Remaining serial job set.
    """
    jobs = []

    t = get_setup_job("firefox.latest", 10)
    t["build_triggers"]="serial.chrome,"+\
                        "serial.firefox.latest,"+\
                        "serial.ie.8"
    jobs.append(t)
    jobs.append(get_test_serial_job("chrome", 9))
    jobs.append(get_test_serial_job("firefox.latest", 8))
    jobs.append(get_test_serial_job("ie.8", 7))

    return jobs


def default_env(ci_home = "/ebs/ci-build/tools"):
    """
    Default environment runs selenium clients on Sauce Labs.
    """
    workspace_dir = ci_home + "/jenkins/.jenkins/jobs/myrepo/workspace"
    return {
        "SELENIUM_SHARED_WORKSPACE" : workspace_dir,
        "TOMCAT_HOME" : workspace_dir + "/thirdparty/tomcat",
        "JUNIT_MAX_MEM" : "2048m",
        "JUNIT_PERM_GEN" : "768m",
        "TOMCAT_MAX_MEM" : "768m",
        "TOMCAT_PERM_GEN" : "512m",
        "ANT_MAX_MEM" : "1024m",
        "ANT_PERM_GEN" : "512m",
        "USE_SAUCELABS" : False,
        "USE_SAUCELABS_TUNNEL" : False,
        "TESTNG_XMX" : "5120",
        "TESTNG_THREADCOUNT" : "50",
        "USE_SAUCELABS" : True,
        "USE_SAUCELABS_TUNNEL" : True,
        "TEST_APP_SERVER" : "test.myrepo.com",
        "SAUCELABS_USERNAME" : "",
        "SAUCELABS_ACCESS_KEY" : "",
        "SAUCELABS_BROWSER" : "googlechrome",
        "SAUCELABS_BROWSER_VERSION" : "",
        "SAUCELABS_OS" : "Windows 2008"
    }


def get_default():
    """
    Standard configuration.
    """
    return {
    "env" : default_env(),
    "os" : "linux",
    "chained": True
    }


def get_integration():
    """
    Integration environment and job set.
    """
    temp = get_default()
    temp["jobs"] = integration_jobs()
    return temp


def get_pre_integration():
    """
    Pre integration environment and job set.
    """
    temp = get_default()
    temp["jobs"] = pre_integration_jobs()
    return temp


def get_serial():
    """
    Serial environment and job set.
    """
    temp = get_default()
    temp["jobs"] = serial_jobs()
    return temp


integration=get_integration()
pre_integration=get_pre_integration()
serial=get_serial()