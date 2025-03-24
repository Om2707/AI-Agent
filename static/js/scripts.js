// Common functionality for all pages
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    setupFormValidation();
    setupFileUploads();
    setupAPIHandlers();
    initializeAIComponents();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation for all forms
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// File upload handling for resumes and other documents
function setupFileUploads() {
    const fileUploads = document.querySelectorAll('.file-upload');
    
    fileUploads.forEach(upload => {
        const fileInput = upload.querySelector('input[type="file"]');
        const fileLabel = upload.querySelector('.file-label');
        const filePreview = upload.querySelector('.file-preview');
        
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                if (this.files && this.files.length > 0) {
                    const fileName = this.files[0].name;
                    if (fileLabel) {
                        fileLabel.textContent = fileName;
                    }
                    
                    // Show preview for PDF files
                    if (filePreview && this.files[0].type === 'application/pdf') {
                        const fileURL = URL.createObjectURL(this.files[0]);
                        filePreview.innerHTML = `<embed src="${fileURL}" type="application/pdf" width="100%" height="200px">`;
                    }
                }
            });
        }
    });
}

// ResumeRanker specific functions
const resumeRanker = {
    rankResumes: async function(jobDescription, resumes) {
        try {
            showLoading('Analyzing resumes with Llama 3.x...');
            
            // Simulate API call to Llama 3.x for resume ranking
            const response = await fetch('/api/rank-resumes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    jobDescription: jobDescription,
                    resumes: resumes
                })
            });
            
            const result = await response.json();
            hideLoading();
            return result;
        } catch (error) {
            hideLoading();
            showError('Error ranking resumes: ' + error.message);
            return [];
        }
    },
    
    displayRankings: function(rankings) {
        const resultsContainer = document.getElementById('ranking-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';
        
        rankings.forEach((candidate, index) => {
            const matchScore = Math.round(candidate.score * 100);
            const cardClass = matchScore > 80 ? 'border-success' : matchScore > 60 ? 'border-warning' : 'border-danger';
            
            const candidateCard = `
                <div class="card mb-3 ${cardClass}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">${index + 1}. ${candidate.name}</h5>
                        <span class="badge bg-${matchScore > 80 ? 'success' : matchScore > 60 ? 'warning' : 'danger'}">
                            ${matchScore}% Match
                        </span>
                    </div>
                    <div class="card-body">
                        <h6>Top Skills Matched:</h6>
                        <ul class="skill-list">
                            ${candidate.matchedSkills.map(skill => `<li>${skill}</li>`).join('')}
                        </ul>
                        <h6>Missing Skills:</h6>
                        <ul class="missing-list">
                            ${candidate.missingSkills.map(skill => `<li>${skill}</li>`).join('')}
                        </ul>
                        <div class="d-flex justify-content-end gap-2 mt-3">
                            <button class="btn btn-sm btn-primary" onclick="emailAutomation.prepareEmail('${candidate.email}', 'interview')">
                                Schedule Interview
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="viewResumeDetails('${candidate.id}')">
                                View Details
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            resultsContainer.innerHTML += candidateCard;
        });
    }
};

// EmailAutomation specific functions
const emailAutomation = {
    templates: {
        interview: {
            subject: "Interview Invitation - [Company Name]",
            body: "Dear [Candidate Name],\n\nWe are pleased to invite you for an interview for the [Job Title] position. Our team was impressed with your qualifications and experience.\n\n[Interview Details]\n\nPlease confirm your availability.\n\nBest regards,\n[Recruiter Name]\n[Company Name]"
        },
        rejection: {
            subject: "Application Status Update - [Company Name]",
            body: "Dear [Candidate Name],\n\nThank you for your interest in the [Job Title] position at [Company Name]. After careful consideration, we have decided to proceed with other candidates whose qualifications better match our current needs.\n\nWe appreciate your time and interest in our company, and we wish you the best in your job search.\n\nBest regards,\n[Recruiter Name]\n[Company Name]"
        },
        offer: {
            subject: "Job Offer - [Job Title] at [Company Name]",
            body: "Dear [Candidate Name],\n\nWe are delighted to offer you the [Job Title] position at [Company Name]. After our interviews and evaluation, we believe your skills and experience make you an excellent fit for our team.\n\n[Offer Details]\n\nPlease review the attached offer letter and let us know your decision by [Response Date].\n\nBest regards,\n[Recruiter Name]\n[Company Name]"
        }
    },
    
    prepareEmail: function(candidateEmail, templateType) {
        const modal = new bootstrap.Modal(document.getElementById('emailModal'));
        const form = document.getElementById('emailForm');
        
        if (form) {
            const subjectField = form.querySelector('#emailSubject');
            const bodyField = form.querySelector('#emailBody');
            const recipientField = form.querySelector('#emailRecipient');
            
            if (recipientField) recipientField.value = candidateEmail || '';
            
            const template = this.templates[templateType] || {subject: '', body: ''};
            
            if (subjectField) subjectField.value = template.subject;
            if (bodyField) bodyField.value = template.body;
        }
        
        modal.show();
    },
    
    sendEmail: async function(recipient, subject, body) {
        try {
            showLoading('Sending email...');
            
            // Simulate API call for sending email
            const response = await fetch('/api/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipient: recipient,
                    subject: subject,
                    body: body
                })
            });
            
            const result = await response.json();
            hideLoading();
            
            if (result.success) {
                showSuccess('Email sent successfully!');
                return true;
            } else {
                showError('Failed to send email: ' + result.message);
                return false;
            }
        } catch (error) {
            hideLoading();
            showError('Error sending email: ' + error.message);
            return false;
        }
    }
};

// InterviewScheduler specific functions
const interviewScheduler = {
    checkAvailability: async function(startDate, endDate) {
        try {
            showLoading('Checking calendar availability...');
            
            // Simulate API call to check calendar availability
            const response = await fetch('/api/check-availability', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    startDate: startDate,
                    endDate: endDate
                })
            });
            
            const result = await response.json();
            hideLoading();
            return result.availableSlots;
        } catch (error) {
            hideLoading();
            showError('Error checking availability: ' + error.message);
            return [];
        }
    },
    
    scheduleInterview: async function(candidateEmail, datetime, duration, interviewers) {
        try {
            showLoading('Scheduling interview...');
            
            // Simulate API call to schedule interview
            const response = await fetch('/api/schedule-interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    candidateEmail: candidateEmail,
                    datetime: datetime,
                    duration: duration,
                    interviewers: interviewers
                })
            });
            
            const result = await response.json();
            hideLoading();
            
            if (result.success) {
                showSuccess('Interview scheduled successfully!');
                return true;
            } else {
                showError('Failed to schedule interview: ' + result.message);
                return false;
            }
        } catch (error) {
            hideLoading();
            showError('Error scheduling interview: ' + error.message);
            return false;
        }
    }
};

// InterviewAgent specific functions
const interviewAgent = {
    currentQuestion: 0,
    questions: [],
    answers: [],
    interviewHistory: [],
    
    startInterview: function(jobTitle, candidateName) {
        this.currentQuestion = 0;
        this.answers = [];
        this.interviewHistory = [];
        
        // Show loading while Llama generates initial questions
        showLoading('Preparing interview questions with Llama 3.x...');
        
        // Simulate API call to get initial questions
        setTimeout(() => {
            this.questions = [
                "Tell me about your background and experience related to this role.",
                "What interests you about this position?",
                "Describe a challenging project you worked on and how you handled it.",
                "How do you stay updated with the latest trends in your field?",
                "Do you have any questions for us?"
            ];
            
            hideLoading();
            this.displayQuestion();
        }, 2000);
    },
    
    displayQuestion: function() {
        const questionContainer = document.getElementById('interview-question');
        const progressBar = document.getElementById('interview-progress');
        
        if (questionContainer) {
            questionContainer.textContent = this.questions[this.currentQuestion];
        }
        
        if (progressBar) {
            const progress = ((this.currentQuestion + 1) / this.questions.length) * 100;
            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `Question ${this.currentQuestion + 1}/${this.questions.length}`;
        }
    },
    
    submitAnswer: async function(answer) {
        this.answers.push(answer);
        this.interviewHistory.push({
            question: this.questions[this.currentQuestion],
            answer: answer
        });
        
        this.currentQuestion++;
        
        if (this.currentQuestion < this.questions.length) {
            this.displayQuestion();
        } else {
            // Interview finished, show completion message
            const interviewContainer = document.getElementById('interview-container');
            const completionContainer = document.getElementById('interview-completion');
            
            if (interviewContainer) interviewContainer.classList.add('d-none');
            if (completionContainer) completionContainer.classList.remove('d-none');
        }
    },
    
    generateAdaptiveQuestion: async function(interviewHistory) {
        try {
            showLoading('Generating follow-up question...');
            
            // Simulate API call to Llama 3.x for adaptive question generation
            const response = await fetch('/api/generate-question', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    interviewHistory: interviewHistory
                })
            });
            
            const result = await response.json();
            hideLoading();
            return result.question;
        } catch (error) {
            hideLoading();
            showError('Error generating question: ' + error.message);
            return "Could you elaborate more on your previous answer?";
        }
    }
};

// HireRecommendationAgent specific functions
const hireRecommendationAgent = {
    analyzeInterview: async function(transcript) {
        try {
            showLoading('Analyzing interview with Llama 3.x...');
            
            // Simulate API call to Llama 3.x for interview analysis
            const response = await fetch('/api/analyze-interview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    transcript: transcript
                })
            });
            
            const result = await response.json();
            hideLoading();
            return result;
        } catch (error) {
            hideLoading();
            showError('Error analyzing interview: ' + error.message);
            return null;
        }
    },
    
    displayRecommendation: function(recommendation) {
        const resultsContainer = document.getElementById('recommendation-results');
        if (!resultsContainer) return;
        
        const strengthsList = recommendation.strengths.map(s => `<li>${s}</li>`).join('');
        const weaknessesList = recommendation.weaknesses.map(w => `<li>${w}</li>`).join('');
        
        const decisionClass = recommendation.decision === 'Hire' ? 'text-success' : 'text-danger';
        
        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Candidate: ${recommendation.candidateName}</h5>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col">
                            <h6>Strengths:</h6>
                            <ul>${strengthsList}</ul>
                        </div>
                        <div class="col">
                            <h6>Areas for Improvement:</h6>
                            <ul>${weaknessesList}</ul>
                        </div>
                    </div>
                    <div class="recommendation-summary">
                        <h5>Summary:</h5>
                        <p>${recommendation.summary}</p>
                    </div>
                    <div class="recommendation-decision text-center mt-4">
                        <h3 class="${decisionClass}">Recommendation: ${recommendation.decision}</h3>
                        <div class="progress mt-2">
                            <div class="progress-bar bg-${recommendation.confidence > 75 ? 'success' : 'warning'}" 
                                 role="progressbar" style="width: ${recommendation.confidence}%">
                                Confidence: ${recommendation.confidence}%
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer d-flex justify-content-end gap-2">
                    <button class="btn btn-outline-secondary" onclick="exportRecommendation('${recommendation.candidateId}')">
                        Export PDF
                    </button>
                    <button class="btn btn-primary" onclick="shareRecommendation('${recommendation.candidateId}')">
                        Share with Team
                    </button>
                </div>
            </div>
        `;
    }
};

// SentimentAnalyzer specific functions
const sentimentAnalyzer = {
    analyzeTranscript: async function(transcript) {
        try {
            showLoading('Analyzing sentiment with Llama 3.x...');
            
            // Simulate API call to Llama 3.x for sentiment analysis
            const response = await fetch('/api/analyze-sentiment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    transcript: transcript
                })
            });
            
            const result = await response.json();
            hideLoading();
            return result;
        } catch (error) {
            hideLoading();
            showError('Error analyzing sentiment: ' + error.message);
            return null;
        }
    },
    
    displayAnalysis: function(analysis) {
        const resultsContainer = document.getElementById('sentiment-results');
        if (!resultsContainer) return;
        
        const emotionData = [
            { emotion: 'Confidence', score: analysis.confidence },
            { emotion: 'Enthusiasm', score: analysis.enthusiasm },
            { emotion: 'Anxiety', score: analysis.anxiety },
            { emotion: 'Hesitation', score: analysis.hesitation },
            { emotion: 'Engagement', score: analysis.engagement }
        ];
        
        let chartsHTML = '';
        
        emotionData.forEach(item => {
            const scoreClass = item.score > 75 ? 'bg-success' : 
                               item.score > 50 ? 'bg-info' : 
                               item.score > 25 ? 'bg-warning' : 'bg-danger';
                               
            chartsHTML += `
                <div class="mb-3">
                    <div class="d-flex justify-content-between">
                        <span>${item.emotion}</span>
                        <span>${item.score}%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar ${scoreClass}" 
                             role="progressbar" style="width: ${item.score}%">
                        </div>
                    </div>
                </div>
            `;
        });
        
        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">Sentiment Analysis Results</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Emotional Indicators:</h6>
                            ${chartsHTML}
                        </div>
                        <div class="col-md-6">
                            <h6>Key Moments:</h6>
                            <ul class="sentiment-moments">
                                ${analysis.keyMoments.map(moment => `
                                    <li>
                                        <span class="timestamp">${moment.timestamp}</span>
                                        <span class="moment-text">${moment.text}</span>
                                        <span class="badge bg-${
                                            moment.sentiment === 'positive' ? 'success' : 
                                            moment.sentiment === 'negative' ? 'danger' : 'secondary'
                                        }">${moment.sentiment}</span>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </div>
                    <div class="sentiment-summary mt-4">
                        <h5>Summary:</h5>
                        <p>${analysis.summary}</p>
                    </div>
                </div>
                <div class="card-footer">
                    <div class="overall-sentiment text-center">
                        <h4>Overall Impression: 
                            <span class="badge bg-${
                                analysis.overallSentiment === 'Very Positive' ? 'success' : 
                                analysis.overallSentiment === 'Positive' ? 'info' : 
                                analysis.overallSentiment === 'Neutral' ? 'secondary' : 
                                analysis.overallSentiment === 'Negative' ? 'warning' : 'danger'
                            }">
                                ${analysis.overallSentiment}
                            </span>
                        </h4>
                    </div>
                </div>
            </div>
        `;
    }
};

// API handling setup
function setupAPIHandlers() {
    // Initialize form submission handlers
    const resumeRankerForm = document.getElementById('resume-ranking-form');
    if (resumeRankerForm) {
        resumeRankerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const jobDescription = document.getElementById('job-description').value;
            const resumeFiles = document.getElementById('resume-files').files;
            
            if (!jobDescription || resumeFiles.length === 0) {
                showError('Please provide a job description and at least one resume');
                return;
            }
            
            // Process form data and call resume ranker function
            const formData = new FormData(this);
            try {
                showLoading('Uploading and processing resumes...');
                
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                hideLoading();
                
                if (result.success) {
                    resumeRanker.displayRankings(result.rankings);
                } else {
                    showError('Error: ' + result.message);
                }
            } catch (error) {
                hideLoading();
                showError('Error: ' + error.message);
            }
        });
    }
    
    // Email form submission handler
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const recipient = document.getElementById('emailRecipient').value;
            const subject = document.getElementById('emailSubject').value;
            const body = document.getElementById('emailBody').value;
            
            if (!recipient || !subject || !body) {
                showError('Please fill in all fields');
                return;
            }
            
            const success = await emailAutomation.sendEmail(recipient, subject, body);
            if (success) {
                // Close modal on success
                const modal = bootstrap.Modal.getInstance(document.getElementById('emailModal'));
                if (modal) modal.hide();
            }
        });
    }
    
    // Interview scheduler form submission handler
    const schedulerForm = document.getElementById('scheduler-form');
    if (schedulerForm) {
        schedulerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const candidateEmail = document.getElementById('candidate-email').value;
            const interviewDate = document.getElementById('interview-date').value;
            const interviewTime = document.getElementById('interview-time').value;
            const duration = document.getElementById('interview-duration').value;
            const interviewers = Array.from(
                document.getElementById('interviewers').selectedOptions
            ).map(option => option.value);
            
            if (!candidateEmail || !interviewDate || !interviewTime || !duration) {
                showError('Please fill in all required fields');
                return;
            }
            
            const datetime = interviewDate + 'T' + interviewTime;
            const success = await interviewScheduler.scheduleInterview(
                candidateEmail, 
                datetime, 
                duration, 
                interviewers
            );
            
            if (success) {
                // Redirect to confirmation page or clear form
                schedulerForm.reset();
            }
        });
    }
    
    // Interview agent form submission handler
    const interviewAnswerForm = document.getElementById('interview-answer-form');
    if (interviewAnswerForm) {
        interviewAnswerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const answerInput = document.getElementById('interview-answer');
            const answer = answerInput.value;
            
            if (!answer) {
                showError('Please provide an answer');
                return;
            }
            
            await interviewAgent.submitAnswer(answer);
            answerInput.value = '';
        });
    }
    
    // Hire recommendation form submission handler
    const recommendationForm = document.getElementById('recommendation-form');
    if (recommendationForm) {
        recommendationForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const transcriptInput = document.getElementById('interview-transcript');
            const transcript = transcriptInput.value;
            
            if (!transcript) {
                showError('Please provide an interview transcript');
                return;
            }
            
            const recommendation = await hireRecommendationAgent.analyzeInterview(transcript);
            if (recommendation) {
                hireRecommendationAgent.displayRecommendation(recommendation);
            }
        });
    }
    
    // Continuation of the sentiment form submission handler that was cut off
const sentimentForm = document.getElementById('sentiment-form');
if (sentimentForm) {
    sentimentForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const transcriptInput = document.getElementById('sentiment-transcript');
        const transcript = transcriptInput.value;
        
        if (!transcript) {
            showError('Please provide an interview transcript');
            return;
        }
        
        const analysis = await sentimentAnalyzer.analyzeTranscript(transcript);
        if (analysis) {
            sentimentAnalyzer.displayAnalysis(analysis);
        }
    });
}

// Initialize AI Components with Llama 3.x
function initializeAIComponents() {
    const llamaVersion = document.getElementById('llama-version');
    if (llamaVersion) {
        llamaVersion.textContent = 'Llama 3.x';
    }
    
    // Add model status indicator
    const modelStatus = document.createElement('div');
    modelStatus.className = 'model-status online';
    modelStatus.innerHTML = '<span class="status-dot"></span> Llama 3.x Online';
    
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        navbar.appendChild(modelStatus);
    }
    
    // Initialize Llama 3.x capabilities display
    displayModelCapabilities();
}

// Display model capabilities
function displayModelCapabilities() {
    const capabilitiesContainer = document.getElementById('model-capabilities');
    if (!capabilitiesContainer) return;
    
    const capabilities = [
        { name: 'Resume Analysis', description: 'Extract and match skills from resumes to job requirements' },
        { name: 'Email Generation', description: 'Create personalized email templates for candidates' },
        { name: 'Interview Q&A', description: 'Generate adaptive interview questions based on candidate responses' },
        { name: 'Decision Making', description: 'Provide hire/no-hire recommendations with confidence scores' },
        { name: 'Sentiment Analysis', description: 'Analyze emotional signals in interview transcripts' }
    ];
    
    let html = '<div class="list-group">';
    capabilities.forEach(cap => {
        html += `
            <div class="list-group-item">
                <h6 class="mb-1">${cap.name}</h6>
                <p class="mb-1 text-muted small">${cap.description}</p>
            </div>
        `;
    });
    html += '</div>';
    
    capabilitiesContainer.innerHTML = html;
}

// Show loading message
function showLoading(message) {
    // Create loading overlay if it doesn't exist
    let loadingOverlay = document.getElementById('loading-overlay');
    if (!loadingOverlay) {
        loadingOverlay = document.createElement('div');
        loadingOverlay.id = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p id="loading-message"></p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }
    
    // Set message and show
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.textContent = message || 'Loading...';
    }
    
    loadingOverlay.classList.add('active');
}

// Hide loading message
function hideLoading() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.remove('active');
    }
}

// Show success message
function showSuccess(message) {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Auto remove after shown
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Show error message
function showError(message) {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Auto remove after shown
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Get or create toast container
function getOrCreateToastContainer() {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    return container;
}

// Export recommendation to PDF
function exportRecommendation(candidateId) {
    showLoading('Generating PDF...');
    
    // Simulate PDF generation
    setTimeout(() => {
        hideLoading();
        showSuccess('Recommendation exported to PDF');
    }, 1500);
}

// Share recommendation with team
function shareRecommendation(candidateId) {
    // Open email modal with recommendation sharing template
    emailAutomation.prepareEmail('team@company.com', 'recommendation');
}

// View detailed resume analysis
function viewResumeDetails(candidateId) {
    showLoading('Loading candidate details...');
    
    // Simulate loading candidate details
    setTimeout(() => {
        hideLoading();
        
        const modal = new bootstrap.Modal(document.getElementById('candidateDetailModal') || createCandidateDetailModal());
        modal.show();
    }, 1000);
}

// Create candidate detail modal if it doesn't exist
function createCandidateDetailModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'candidateDetailModal';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'candidateDetailModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="candidateDetailModalLabel">Candidate Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="candidate-profile mb-4">
                        <h4>John Doe</h4>
                        <p class="text-muted">Senior Software Engineer</p>
                        <div class="d-flex gap-3 mb-3">
                            <span><i class="bi bi-envelope"></i> john.doe@example.com</span>
                            <span><i class="bi bi-telephone"></i> (555) 123-4567</span>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Skills Analysis</h5>
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h6>Technical Skills</h6>
                                    <div class="skill-match">
                                        <span>Python</span>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" style="width: 95%">95%</div>
                                        </div>
                                    </div>
                                    <div class="skill-match">
                                        <span>JavaScript</span>
                                        <div class="progress">
                                            <div class="progress-bar bg-success" style="width: 85%">85%</div>
                                        </div>
                                    </div>
                                    <div class="skill-match">
                                        <span>Machine Learning</span>
                                        <div class="progress">
                                            <div class="progress-bar bg-warning" style="width: 65%">65%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h5>Experience Match</h5>
                            <div class="card">
                                <div class="card-body">
                                    <h6>Key Requirements</h6>
                                    <ul class="requirement-list">
                                        <li class="matched">5+ years of software development</li>
                                        <li class="matched">Experience with Python</li>
                                        <li class="partial">Experience with AI/ML</li>
                                        <li class="missing">Cloud platform experience</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="resume-preview mt-4">
                        <h5>Resume Preview</h5>
                        <div class="card">
                            <div class="card-body">
                                <p class="text-muted">Resume content preview would appear here</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="emailAutomation.prepareEmail('john.doe@example.com', 'interview')">Schedule Interview</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    return modal;
}

// Add Llama specific headers to all fetch requests
const originalFetch = window.fetch;
window.fetch = function() {
    if (arguments[1] && arguments[1].headers) {
        arguments[1].headers = {
            ...arguments[1].headers,
            'X-Llama-Version': 'Llama-3.x'
        };
    }
    return originalFetch.apply(this, arguments);
};