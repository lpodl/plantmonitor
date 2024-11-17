pipeline {
    agent any
    
    environment {
        CONDA_PATH = "/home/justin/miniconda3"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Generate Static Site') {
            steps {
                script {
                    sh '''
                        cd /home/justin/plantmonitor/plantmonitor/plantmon/website
                        source "${CONDA_PATH}/etc/profile.d/conda.sh"
                        conda activate plantmon
                        python freeze.py
                    '''
                }
            }
        }
        
        stage('Prepare Static Files') {
            steps {
                sh '''
                    cd build
                    mv plantmonitor-dynamic index.html
                    find . -type f -not \\( -name 'index.html' -or -name 'plantmon.css' \\) -delete
                    find . -type d -empty -delete
                '''
            }
        }
        
        stage('Deploy to Static Repo') {
            steps {
                sh '''
                    # Copy files to static repo
                    cp -r build/index.html build/plantmon.css ~/plantmonitor-static/
                    cd /home/justin/plantmonitor-static
                    git add .
                    git commit -m "Update from Jenkins: $(date '+%Y-%m-%d %H:%M')"
                    git push origin main
                '''
            }
        }
    }
    
    post {
        failure {
            echo 'Pipeline failed. Check the logs for details.'
        }
        success {
            echo 'Static site successfully generated and deployed!'
        }
    }
}
