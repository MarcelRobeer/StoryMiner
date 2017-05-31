import base64
import json
import spacy

# Holds the system name and set of user stories, can be exported
class UserStorySet(object):
	def __init__(self, nlp, systemname):
		self.system = WithMain()
		self.system.main = nlp(systemname)[0]
		self.set = []

	def toJSON(self):
		[us.export() for us in self.set]
		return json.dumps(self, default=self.help, ensure_ascii=False, indent=4)

	def help(self, o):
		if type(o) is spacy.tokens.doc.Doc:
			return base64.encodestring(o.to_bytes()).decode('ascii')
		elif type(o) is spacy.tokens.token.Token:
			return o.text
		elif type(o) is spacy.tokens.span.Span:
			return o.text
		elif type(o) is bytes:
			return
		return o.__dict__

# Contains a single user story
class UserStory(object):
	def __init__(self, nr, text, no_punct):
		self.id = nr
		self.text = text
		self.sentence = no_punct
		self.iloc = []
		self.role = Role()
		self.means = Means()
		#self.ends = Ends()
		self.has_ends = False

	def export(self):
		if self.role:
			self.role.text = self.role.doc.text
			self.role.doc_t = " ".join(["{}/{}".format(t.text, t.pos_) for t in self.role.doc])
		if self.means:
			self.means.text = self.means.doc.text
			self.means.doc_t = " ".join(["{}/{}".format(t.text, t.pos_) for t in self.means.doc])
		if self.has_ends and self.ends:
			self.ends.text = self.ends.doc.text
			self.ends.doc_t = " ".join(["{}/{}".format(t.text, t.pos_) for t in self.ends.doc])

	def txtnr(self):
		return "US" + str(self.id)

	def is_func_role(self, token):
		if token.i in self.iloc:
			return True
		return False

class FailedUserStory(object):
	def __init__(self, nr, text, error):
		self.id = nr
		self.text = text
		self.error = error

	def export(self):
		return

class UserStoryPart(object):
	def __init__(self):
		self.doc = []
		self.t = ""
		self.simplified = ""
		self.indicator = []
		self.indicator_t = ""
		self.indicator_i = -1

class FreeFormUSPart(UserStoryPart):
	def __init__(self):
		self.main_verb = WithMain()
		self.main_object = WithMain()
		self.subject = WithMain()
		#self.free_form = []
		#self.verbs = []
		#self.phrasal_verbs = []
		#self.nouns = []
		#self.proper_nouns = []
		#self.noun_phrases = []
		#self.compounds = []

class Role(UserStoryPart):
	def __init__(self):
		self.functional_role = WithMain()

class Means(FreeFormUSPart):
	pass

class Ends(FreeFormUSPart):
	pass

class WithMain(object):
	def __init__(self):
		self.main = []
		#self.phrase = []
		#self.compound = []
		#self.type = ""

	def get(self):
		if hasattr(self, 'phrase'):
			return [x for x in self.phrase]
		return [self.main]
			