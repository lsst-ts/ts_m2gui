#!/usr/bin/env groovy

pipeline {

    agent {
        // Use the docker to assign the Python version.
        // Use the label to assign the node to run the test.
        // It is recommended by SQUARE team do not add the label to let the
        // system decide.
        docker {
          image 'lsstts/develop-env:develop'
          args "-u root --entrypoint=''"
        }
    }

    options {
      disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H * * * *')
    }

    environment {
        // SAL setup file
        SAL_SETUP_FILE = "/home/saluser/.setup.sh"
        // XML report path
        XML_REPORT = "jenkinsReport/report.xml"
        // Module name used in the pytest coverage analysis
        MODULE_NAME = "lsst.ts.m2gui"
        // PlantUML url
        PLANTUML_URL = "https://github.com/plantuml/plantuml/releases/download/v1.2021.13/plantuml-1.2021.13.jar"
        // Branch name. This is to deal with the condition that the env.BRANCH_NAME
        // will become "PR-X" at the pull request. When that happens, only the
        // env.CHANGE_BRANCH will give the expected name.
        BRANCH = getBranchName(env.CHANGE_BRANCH, env.BRANCH_NAME)
        // Authority to publish the document online
        user_ci = credentials('lsst-io')
        LTD_USERNAME = "${user_ci_USR}"
        LTD_PASSWORD = "${user_ci_PSW}"
        DOCUMENT_NAME = "ts-m2gui"
    }

    stages {

        stage('Cloning Repos') {
            steps {
                withEnv(["WORK_HOME=${env.WORKSPACE}"]) {
                    sh """
                        git clone https://github.com/lsst-ts/ts_m2com.git

                        cd ${WORK_HOME}/ts_m2com
                        git checkout -t origin/${env.BRANCH} | true
                    """
                }
            }
        }

        stage('Unit Tests and Coverage Analysis') {
            steps {
                // Pytest needs to export the junit report.
                withEnv(["WORK_HOME=${env.WORKSPACE}"]) {
                    sh """
                        source ${env.SAL_SETUP_FILE}

                        cd ${WORK_HOME}/ts_m2com
                        setup -k -r .

                        cd ${WORK_HOME}
                        setup -k -r .
                        pytest tests/ --cov-report html --cov=${env.MODULE_NAME} --junitxml=${env.XML_REPORT}
                    """
                }
            }
        }

        stage('Build the Document and Upload') {
            steps {
                // Pytest needs to export the junit report.
                withEnv(["WORK_HOME=${env.WORKSPACE}"]) {
                    sh """
                        source ${env.SAL_SETUP_FILE}

                        pip install sphinxcontrib-plantuml ltd-conveyor

                        curl -L ${env.PLANTUML_URL} -o plantuml.jar
                        export PATH_PLANTUML=${env.WORK_HOME}/plantuml.jar

                        cd ${WORK_HOME}/ts_m2com
                        setup -k -r .

                        cd ${WORK_HOME}
                        setup -k -r .

                        package-docs build
                        ltd upload --product ${env.DOCUMENT_NAME} --git-ref ${env.BRANCH_NAME} --dir doc/_build/html
                    """
                }
            }
        }

    }

    post {
        always {
            // The path of xml needed by JUnit is relative to
            // the workspace.
            junit "${env.XML_REPORT}"

            // Publish the HTML report
            publishHTML (target: [
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: "Coverage Report"
            ])
        }

        cleanup {
            // Change the ownership of workspace to Jenkins for the clean up
            // This is to work around the condition that the user ID of jenkins
            // is 1003 on TSSW Jenkins instance. In this post stage, it is the
            // jenkins to do the following clean up instead of the root in the
            // docker container.
            withEnv(["WORK_HOME=${env.WORKSPACE}"]) {
                sh 'chown -R 1003:1003 ${WORK_HOME}/'
            }

            // clean up the workspace
            deleteDir()
        }
    }
}

// Return branch name. If changeBranch isn't defined, use branchName.
def getBranchName(changeBranch, branchName) {
    def branch = (changeBranch == null) ? branchName : changeBranch
    return branch
}
