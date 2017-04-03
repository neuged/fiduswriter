from tornado.web import RequestHandler, asynchronous, HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat
from tornado.escape import json_decode
from base.django_handler_mixin import DjangoHandlerMixin
from urllib import urlencode
from .models import Journal, Submission, SubmissionRevision, Author, Reviewer
from django.core.files.base import ContentFile
from document.models import Document


class OJSProxy(DjangoHandlerMixin, RequestHandler):
    @asynchronous
    def get(self, relative_url):
        user = self.get_current_user()
        if not user.is_authenticated():
            self.set_status(401)
            return
        if relative_url == 'journals':
            base_url = self.get_argument('url')
            key = self.get_argument('key')
        else:
            return
        plugin_path = \
            '/index.php/index/gateway/plugin/FidusWriterGatewayPlugin/'
        url = base_url + plugin_path + relative_url
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                url_concat(url, {'key': key}),
                'GET'
            ),
            callback=self.on_get_response
        )

    # The response is asynchronous so that the getting of the data from the OJS
    # server doesn't block the FW server connection.
    def on_get_response(self, response):
        if response.error:
            raise HTTPError(500)
        self.write(response.body)
        self.finish()

    @asynchronous
    def post(self, relative_url):
        self.user = self.get_current_user()
        if not self.user.is_authenticated():
            self.set_status(401)
            self.finish()
            return
        self.plugin_path = \
            '/index.php/index/gateway/plugin/FidusWriterGatewayPlugin/'
        if relative_url == 'author_submit':
            self.author_submit()
        elif relative_url == 'reviewer_submit':
            self.reviewer_submit()
        else:
            self.set_status(401)
            self.finish()
            return

    def author_submit(self):
        # Submitting a new submission revision.
        document_id = self.get_argument('doc_id')
        revisions = SubmissionRevision.objects.filter(
            document_id=document_id
        )
        if len(revisions) == 0:
            # The document is not part of an existing submission.
            journal_id = self.get_argument('journal_id')
            self.submission = Submission()
            self.submission.submitter = self.user
            self.submission.journal_id = journal_id
            # Save the attached file as the submission file, transforming it
            # from the python file_object format Tornado provides it in to the
            # format used by Django.
            file_object = self.request.files['file'][0]
            self.submission.file_object.save(
                file_object.filename,
                ContentFile(file_object.body),
                save=False
            )
            self.submission.save()
            # Create two revisions:
            # - 0: this is the submitted file that should not be changed
            # - 1: this is the submitted file, but this version can be changed
            # by an editor to become the first review file.
            self.revision = SubmissionRevision()
            self.revision.submission = self.submission
            self.revision.version = "1.0.0"
            version = "1.0.0"
            # Connect a new, empty document to the submission.
            document = Document()
            journal = Journal.objects.get(id=journal_id)
            document.owner = journal.editor
            document.save()
            self.revision.document = document
            self.revision.save()
        else:
            revision = revisions[0]
            self.submission = revision.submission
            if self.submission.submitter != self.user:
                # Trying to submit revision for submission of other user
                self.set_status(401)
                self.finish()
                return
            version = revision.version

        fidus_url = '{protocol}://{host}'.format(
            protocol=self.request.protocol,
            host=self.request.host
        )

        title = self.get_argument('title')
        post_data = {
            'username': self.user.username,
            'title': title,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            'affiliation': 'some affiliation',
            'author_url': 'some author_url',
            'journal_id': journal.ojs_jid,
            'fidus_url': fidus_url,
            'fidus_id': self.submission.id,
            'version': version
        }

        if version != "1.0.0":
            post_data['ojs_id'] = self.submission.ojs_jid
        body = urlencode(post_data)
        key = journal.ojs_key
        base_url = journal.ojs_url
        url = base_url + self.plugin_path + 'authorSubmit'
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                url_concat(url, {'key': key}),
                'POST',
                None,
                body
            ),
            callback=self.on_author_submit_response
        )

    # The response is asynchronous so that the getting of the data from the OJS
    # server doesn't block the FW server connection.
    def on_author_submit_response(self, response):
        if response.error:
            self.revision.document.delete()
            self.revision.delete()
            raise HTTPError(500)
        # If this is the first revision (version==1.0.0), then set the
        # submission ID from the response from the OJS server.
        if self.revision.version == "1.0.0":
            json = json_decode(response.body)
            self.submission.ojs_jid = json['submission_id']
            self.submission.save()
            # We save the author ID on the OJS site. Currently we are NOT using
            # this information for login purposes.
            Author.objects.create(
                user=self.user,
                submission=self.submission,
                ojs_jid=json['user_id']
            )

        self.write(response.body)
        self.finish()

    def reviewer_submit(self):
        # Submitting a new submission revision.
        document_id = self.get_argument('doc_id')
        reviewers = Reviewer.objects.filter(
            revision__document_id=document_id,
            user=self.user
        )
        if len(reviewers) == 0:
            # Trying to submit review without access rights.
            self.set_status(401)
            self.finish()
        reviewer = reviewers[0]
        post_data = {
            'submission_id': reviewer.revision.submission.ojs_jid,
            'version': reviewer.revision.version,
            'user_id': reviewer.ojs_jid,
            'editor_message': self.get_argument('editor_message'),
            'editor_author_message': self.get_argument('editor_author_message')
        }

        body = urlencode(post_data)
        key = reviewer.revision.submission.journal.ojs_key
        base_url = reviewer.revision.submission.journal.ojs_url
        url = base_url + self.plugin_path + 'reviewerSubmit'
        http = AsyncHTTPClient()
        http.fetch(
            HTTPRequest(
                url_concat(url, {'key': key}),
                'POST',
                None,
                body
            ),
            callback=self.on_reviewer_submit_response
        )

    # The response is asynchronous so that the getting of the data from the OJS
    # server doesn't block the FW server connection.
    def on_reviewer_submit_response(self, response):
        if response.error:
            self.revision.document.delete()
            self.revision.delete()
            raise HTTPError(500)

        self.write(response.body)
        self.finish()
