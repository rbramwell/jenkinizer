from jinja2 import *
from optparse import OptionParser
import shutil
import os
import sys
import tempfile
import tarfile


class ServerOptionParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
        self.add_option("-t", "--jenkins-type", action="store", dest="jenkins_type", default="selenium",
                         help="Type of server to generate." )
        self.add_option("-j", "--jenkins-jobset", dest="jenkins_jobset", default="integration",
                          help="Specific host this Jenkins will be deployed to.")
        self.add_option("-o", "--install-dir", dest="install_dir", default="/ebs/ci-build/tools/jenkins",
                          help="Location to install the newly generated server.")
        self.add_option("-b", "--jenkins-branch", dest="jenkins_branch", default="release",
                          help="Branch to use in testing.")
        self.add_option("-e", "--recipient-email", dest="recipient_email", default=" ",
                          help="Email recipient")
        self.add_option("-d", "--discard-old-builds", action="store_true", dest="discard_old_builds", default=False,
                          help="If set, old builds will be discarded.")


def make_selected_archive(backup_file_name, base_dir, files, gzip = True):
    backup_file = tarfile.open(backup_file_name, 'w:gz' if gzip else "w")
    current_dir = os.getcwd()
    os.chdir(base_dir)
    for artifact in files:
        if os.path.exists(artifact):
            backup_file.add(artifact)
    backup_file.close()
    os.chdir(current_dir)


def restore_archive(backup_file_name, base_dir, gzip = True):
    backup_file = tarfile.open(backup_file_name, "r:gz" if gzip else "r")
    backup_file.extractall(base_dir)
    backup_file.close()


def backup_old_builds(jobs_dir, job_names):
    archives = {}
    for job in job_names:
        job_dir = jobs_dir + "/" + job
        if os.path.exists(job_dir):
            print "Backing up old builds in %s" % (job_dir)
            backup_file_name = tempfile.gettempdir() + "/" + job + ".tar.gz"
            make_selected_archive(backup_file_name, job_dir, ["./builds", "./lastStableBuild", "./lastSuccessfulBuild", "./nextBuildNumber"])
            archives[job] = backup_file_name
    return archives


def build_server(options, base_path = os.getcwd()):

    # We categorize Jenkins instances depending on the jobs they run.  We have Jenkins instances that run selenium,
    # run unit and functional tests, build artifacts and deploy artifacts. This defined the kind of Jenkins we are
    # deploying.
    jenkins_type = options.jenkins_type
    
    # The set of jobs to deploy.
    jenkins_jobset = options.jenkins_jobset
    
    # The location to install this Jenkins instance to on the filesystem.
    install_dir = options.install_dir

    # Email.
    recipient_email = options.recipient_email

    # Make our python job and server configuration files reachable.
    sys.path.extend([base_path + "/config/servers"])

    # Define the template environment.
    template_env = Environment(loader=FileSystemLoader(base_path + '/config/templates/' + jenkins_type + '/'))
    
    # Import the specific server and job data for this jenkins type
    # and this jobset.
    server_config = __import__(jenkins_type).__dict__[jenkins_jobset]
    server_config["env"]["EMAIL"] = recipient_email
    server_config["env"]["BRANCH"] = options.jenkins_branch

    jenkins_dir = install_dir + "/.jenkins"
    jobs_dir = jenkins_dir + "/jobs"


    # Backup archived files and
    # remove the old instance if it exists.
    archives = {}
    if os.path.exists(install_dir):
        if not options.discard_old_builds:
            archives = backup_old_builds(jobs_dir, [job["job_name"] for job in server_config["jobs"]])
        shutil.rmtree(install_dir)

    # Copy all of the static Jenkins files to the installation directory
    shutil.copytree(base_path + "/install", install_dir)

    print "Generating configuration for jenkins type %s (writing to %s)" % (jenkins_type, install_dir)

    # Create the jenkins main config file.
    with open(jenkins_dir + "/config.xml", "w") as f:
        t = template_env.get_template("server-config.xml")
        f.write(t.render(server_config))

    # Create the jobs config files.
    for job in server_config["jobs"]:
        job_name = job[ "job_name"]
        job_template = job["template_file" ]
        job.update(server_config)

        print "Creating job %s from %s" % (job_name, job_template)
        job_dir = jobs_dir + "/" + job_name
        os.makedirs(job_dir)
        with open(job_dir + "/config.xml", "w") as f:
            t = template_env.get_template(job_template)
            f.write(t.render(job))

        if archives.has_key(job_name):
            print "Restoring old builds for %s" % (job_name)
            restore_archive(archives[job_name], job_dir)





# Parse options.
parser = ServerOptionParser()
(options, args) = parser.parse_args()

# Generate the files.
build_server(options)