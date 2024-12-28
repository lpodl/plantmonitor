pipeline {
    agent any
    triggers {
        cron('10 * * * *')
    }
    stages {
        stage('Print Trigger Cause') {
            steps {
                script {
                    def causes = currentBuild.getBuildCauses()
                    echo "Build was triggered by: ${causes}"
                }
            }
        }

        stage('Checkout') {
            steps {
                script {
                    // Checkout dynamic repo
                    checkout scm
                    
                    // Clone static repo
                    sh '''
                        rm -rf ~/plantmonitor-static
                        cd ~
                        git clone https://github.com/lpodl/plantmonitor-static.git
                    '''
                }
            }
        }
        
        stage('Generate Static Site') {
            steps {
                script {
                    sh '''
                        cd ./plantmon/website
                        /var/lib/jenkins/miniconda3/condabin/conda run -n plantmon python freeze.py
                    '''
                }
            }
        }
        
        stage('Prepare Static Files') {
            steps {
                sh '''
                    # delete everything but html and css for plantmonitor
                    cd ./plantmon/website/build
                    mv plantmonitor-dynamic index.html
                    find . -type f -not \\( -name 'index.html' -or -name 'plantmon.css' \\) -delete
                    find . -type d -empty -delete
                '''
            }
        }
        
        stage('Deploy to Static Repo') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'gh-plantmon-accesstoken', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_PASSWORD')]) {
                    sh '''
                        cd ./plantmon/website/build
                        # Copy files to static repo
                        cp -r ./index.html ./static/ ~/plantmonitor-static
                        cd  ~/plantmonitor-static
                        git add .
                        git status
                        git commit -m "Update from Jenkins: $(date '+%Y-%m-%d %H:%M')"
                        git push https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/lpodl/plantmonitor-static.git
                    '''
                }
            }
        }

        stage('Clean Up') {
            steps {
                sh '''
                    rm -rf ~/plantmonitor-static
                '''
            }
        }
    }                       

    post {
        always {
            cleanWs()
        }
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
        success {
            echo 'Static site successfully generated and deployed!'
        }
    }
}
