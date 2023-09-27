import enum
import os
import re
import time
import datetime
import traceback

from query_frame import QueryFrame
from ulf_parser import ULFParser
from constraint_solver import *
import utils
from bw_planner import Planner

MISSPELLS = [
  (' book', ' block'), (' blog', ' block'), (' black', ' block'), (' walk', ' block'), (' wok', ' block'),
  (' lock', ' block'), (' vlog', ' block'), (' blocked', ' block'), (' glock', ' block'), (' look', ' block'),
  (' talk', ' block'), (' cook', ' block'), (' clock', ' block'), (' plug', ' block'), (' logo', ' block'), (' boxer', ' blocks are'),
  (' blonde', ' block'), (' blow', ' block'), (' bloke', ' block'), (' dog', ' block'),
  (' involved', ' above'), (' about', ' above'), (' patching', ' touching'), (' catching', ' touching'),
  (' cashing', ' touching'), (' flashing', ' touching'), (' flushing', ' touching'),(' fashion', ' touching'), (' patch', ' touch'),
  (' thatching', ' touching'), (' trash in', ' touching'), (' tracking', ' touching'),
  (' in a cup', ' on top'), (' after the right', ' are to the right'), 
  (' merced us', ' mercedes'), (' messages', ' mercedes'), (' mercer does', ' mercedes'), (' merced is', ' mercedes'),
  (' critter', ' twitter'), (' butcher', ' twitter'), (' treetop', ' twitter'), (' toilet', ' twitter'), (' trader', ' twitter'),
  (' front mount', ' frontmost'),
  (' grimlock', ' green block'),
  (' where\'s', ' where is'),
  (' attaching', ' touching'),
  (' talking block', ' target block'), (' chopping', ' target'), (' testicle', ' texaco'),
  (' merciless', ' mercedes'),
  (' mug', ' block'), (' the find', ' behind'),
  (' touches', ' touch'), (' at top', ' on top'), (' stretching', ' is touching'),
  (' to be right', ' to the right'), (' for the rights', ' to the right'), 
  (' in the table', ' on the table'),
  (' top most', ' topmost'), (' right most', ' rightmost'), (' left most', ' leftmost'), (' front most', ' frontmost'),
  (' back most', ' backmost'), (' back-most', ' backmost'),
  (' top-most', ' topmost'), (' right-most', ' rightmost'), (' right move', ' rightmost'), (' left-most', ' leftmost'), (' front-most', ' frontmost'),
  (' song', ' some'), (' sound', ' some'), (' sun', ' some'),
  (' hyatt', ' highest'), (' hyve', ' highest'), (' hive', ' highest'), (' louis', ' lowest'), 
  (' father\'s', ' farthest'), (' father', ' farthest'),
  (' gridlock', ' green block'), (' rim ', ' green '), (' siri', ' david'), (' date it', ' david'),
  (' grimblock', ' green block'), (' redlock', ' red block'), (' rap ', ' red '), (' ramp ', ' red '),
  (' ram block', ' red block'), (' to other', ' two other'), (' lava the', ' above the'), (' watch', ' touch'),
  (' phase', ' face'), (' passing', ' touching'), (' 3 ', ' three '), 
  (' to bl', ' two bl'), (' to red', ' two red'), (' to gre', ' two gre'), ('what colors', 'what color'),
  (' rad', ' red'), (' rand', ' red'), 
  ('what\'s ', 'what is '),
  (' sims', ' since'), (' sings', ' since'), (' love', ' block'), (' globe', ' block'), (' is starting', ' is touching'), 
  (' passed', ' has'), (' pass', ' has'), (' paused', ' has'),
  (' did they', ' did i'), (' have they', ' have i'),
  (' 2 ', ' two '), (' 3 ', ' three '), (' to moves', ' two moves')
]


class HCIManager(object):
  """Manages the high-level interaction loop between the user and the system."""

  class STATE(enum.Enum):
    """Enumeration of all the states that the system can assume."""
    INIT = 0
    SYSTEM_GREET = 1
    USER_GREET = 2
    QUESTION_PENDING = 3		
    USER_BYE = 4
    END = 5
    SUSPEND = 6
    TUTORING_BEGIN = 7

  def __init__(self, world):

    #Stores the context of the conversation. For future use.
    self.context = None

    #Current state = initial state
    self.state = self.STATE.INIT

    #User's latest speech piece
    self.current_input = ""

    self.eta_path = ".." + os.sep + "eta" + os.sep
    self.eta_io = ".." + os.sep + "eta" + os.sep + "io" + os.sep + "david-qa" + os.sep
    self.eta_input = self.eta_path + "input.lisp"		
    self.eta_ulf = self.eta_path + "ulf.lisp"
    self.eta_answer = self.eta_path + "answer.lisp"
    self.eta_output = self.eta_io + "output.txt"
    self.eta_perceptions = self.eta_path + "perceptions.lisp"
    self.eta_goal_req = self.eta_path + "goal-request.lisp"
    self.eta_goal_resp = self.eta_path + "goal-rep.lisp"
    self.eta_planner_input = self.eta_path + "planner-input.lisp"
    self.eta_user_try_success = self.eta_path + "user-try-ka-success.lisp"

    self.eta_perceptions_in = self.eta_io + "in" + os.sep + "Blocks-World-System.lisp"
    self.eta_audio_in = self.eta_io + "in" + os.sep + "Audio.lisp"
    self.eta_text_in = self.eta_io + "in" + os.sep + "Text.lisp"
    self.eta_spatial_in = self.eta_io + "in" + os.sep + "Spatial-Reasoning-System.lisp"

    self.eta_perceptions_out = self.eta_io + "out" + os.sep + "Blocks-World-System.lisp"		
    self.eta_text_out = self.eta_io + "out" + os.sep + "Text.lisp"
    self.eta_spatial_out = self.eta_io + "out" + os.sep + "Spatial-Reasoning-System.lisp"

    self.coords_log_path = "logs" + os.sep + "session_coords_data"
    self.dialog_log_path = "logs" + os.sep + "dialog_log"
    self.log_file = None

    self.world = world
    self.ulf_parser = ULFParser()
    self.planner = Planner(self.world)
    
    self.last_mentioned = []
    self.state = self.STATE.INIT

    self.dialog_counter = 0

  def get_speech_ulf(self, speech_text):
    return "(setq *input* '((^you say-to.v ^me \"" + speech_text + "\")))"
  
  def send_to_eta(self, mode, text):
    if mode == "INPUT":
      filename = self.eta_audio_in
      formatted_msg = self.get_speech_ulf(text)
    elif mode == "GOAL_RESP":
      filename = self.eta_spatial_in
      formatted_msg = "(setq *goal-rep* '" + text + ")"
    elif mode == "PLAN_STEP":
      filename = self.eta_spatial_in
      formatted_msg = "(setq planner-input '" + text + ")"
    else:
      filename = self.eta_spatial_in
      if text != "\'None":
        formatted_msg = "(setq *input* \'(" + text + "))"
      else: 
        formatted_msg = "(setq *input* " + text + ")"
    
    print("SENT TO ETA: ", formatted_msg)
    with open(filename, 'w') as file:
      file.write(formatted_msg)

  def read_from_eta(self, mode):
    filename = ""
    if mode == "ULF":
      filename = self.eta_spatial_out
    elif mode == "GOAL_REQ":
      filename = self.eta_spatial_out
    else:			
       filename = self.eta_output

    attempt_counter = 0
    with open(filename, "r+") as file:
      msg = ""
      while msg is None or msg == "":
        time.sleep(0.3)
        msg = file.readlines()
        attempt_counter += 1
        if attempt_counter == 40:
          break
      file.truncate(0)

    if msg == "" or msg is None or msg == []:
      return None
    elif mode == "ULF":
      result = "".join([line for line in msg])
      result = re.sub(" +", " ", result.replace("\n", ""))
      result = (result.split("* '")[1])[:-1]
      self.log("ULF", result)
    elif mode == "GOAL_REQ":
      msg = "".join(msg)
      msg = msg.split("*chosen-obj-schema*")[1].strip()[1:-1]
      return msg
    else:
      result = ""
      responses = [r.strip() for r in msg if r.strip() != ""]
      for resp in responses:
        if "*" not in resp and ": ANSWER" in resp:
          result += resp.split(":")[2]
        elif "*" not in resp and ": " in resp and "DO YOU HAVE A SPATIAL QUESTION" not in resp and "NIL" not in resp:
          result += resp.split(":")[1]			

    return result
  
  def clear_file(self, filename):
    open(filename, 'w').close()

  def read_and_vocalize_from_eta(self):
    response = self.read_from_eta(mode = "OUTPUT")		
    if response != "" and response is not None:
      print ("\n\033[1;34;40mDAVID: " + str(response) + "\033[0;37;40m\n")
      self.log("DAVID", response)		
    return response

  def log(self, mode, text):
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%H:%M:%S")
    self.world.log_event(mode, text)
    with open(self.dialog_log_path, "a+") as logf:
      logf.write(dt_str + " " + str(mode) + ": " + str(text) + "\n")		

  def log_coords(self, coords):
    with open(self.coords_log_path, "a+") as logf:
      logf.write("\n" + coords + "\n")

  def init_log(self):
    with open(self.dialog_log_path, "a+") as logf:
      logf.write("\nSESSION: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
      logf.write("=============================================================\n")		

    with open(self.coords_log_path, "a+") as logf:
      logf.write("\nSESSION: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
      logf.write("=============================================================\n")		

  def send_perceptions(self):
    """
    (
    (|Toyota| at-loc.p ($ loc 0 0 0))
    (|Twitter|) ((past move.v) (from.p-arg ($ loc 0 0 0)) (to.p-arg ($ loc 1 1 1))))
    )

    (setq next-answer 'None) for no relation satisfying the query """
    
    assert self.world.history is not None and len(self.world.history) > 0

    loc_dict = self.world.history[-1].locations
    locations = ['(' + self.world.find_entity_by_name(name).get_ulf() + ' at-loc.p ' + \
        utils.loc_to_ulf(loc_dict[name]) + ')' for name in loc_dict]
    moves = self.world.get_move_ulfs_after_checkpoint()
    
    perceptions = "(setq *next-perceptions* \'(" + " ".join(locations + moves) + "))"
    print ("PERCEPTIONS: ", perceptions)
    self.log_coords(perceptions)
    with open(self.eta_perceptions_in, 'w') as f:
      f.write(perceptions)
    self.world.make_checkpoint()
  
  def get_ulf(self, query_frame, subj_list, obj_list):
    if subj_list is None or len(subj_list) == 0:
      return '\'None'
    ret_val = ''
    rel = None
    if query_frame.predicate is not None:
      rel = query_frame.predicate.content
      is_neg = query_frame.predicate.neg
      for mod in query_frame.predicate.mods:
        is_neg |= type(mod) == TNeg
      if is_neg:
        rel = 'not ' + rel
      #print ("ANS DATA: ", subj_list, rel, obj_list)
    print ("ANSWER SET DATA: ", subj_list, obj_list)
    if rel is not None and type(rel) != TCopulaBe and obj_list != None and len(obj_list) > 0 and type(obj_list[0]) == tuple and query_frame.query_type != query_frame.QueryType.ATTR_COLOR and query_frame.query_type != query_frame.QueryType.DESCR and query_frame.query_type != query_frame.QueryType.COUNT:
      self.last_mentioned = []
      for subj in subj_list:				
        if type(subj[0]) == Entity:
          self.last_mentioned.append(subj[0])
          for obj in obj_list:
            if type(obj[0][0]) == Entity:					
              ret_val += '((that (' + subj[0].get_ulf() + ' ' + rel + ' ' + obj[0][0].get_ulf()+ ')) certain-to-degree ' + str(subj[1] * obj[1]) + ') '
            else:
              ret_val += '(' + subj[0].get_ulf() + ' ' + str(subj[1]) + ') '
    elif query_frame.query_type == query_frame.QueryType.DESCR: 
      for item in obj_list:
        item = item[0][0]
        #print ("WHERE: ", item)
        self.last_mentioned = [item[1][0][0]]
        if len(item[1][0]) == 2:
          ret_val += '((that (' + item[1][0][0].get_ulf() + ' ' + item[0] + ' ' + item[1][0][1].get_ulf() + ')) certain-to-degree ' + str(item[1][1]) + ') '
        elif len(item[1][0]) == 3:
          ret_val += '((that (' + item[1][0][0].get_ulf() + ' ' + item[0] + ' ' + item[1][0][1].get_ulf() + ' ' + item[1][0][2].get_ulf() + ')) certain-to-degree ' + str(item[1][1]) + ') '
    else:
      self.last_mentioned = [subj[0] for subj in subj_list]
      for subj in subj_list:
        ret_val += '((' + subj[0].get_ulf() + ') ' + str(subj[1]) + ')'
    ret_val = ret_val.replace('McDonald\'s', 'McDonalds')
    return ret_val

  def preprocess(self, input):
    input = input.lower()
    
    for misspell, fix in MISSPELLS:
      input = input.replace(misspell, fix)
    return input

  def start(self):
    """Initiate the listening loop."""

    self.clear_file(self.eta_ulf)
    self.clear_file(self.eta_answer)
    self.clear_file(self.eta_input)
    #self.clear_file(self.coords_log_path)
    self.init_log()

    print ("\n==========================================================")
    print ("Starting the dialog loop...")
    print ("==========================================================\n")
    
    while True:
      
      if self.state == self.STATE.INIT:				
        response = self.read_and_vocalize_from_eta()				
        if response is None:
          continue

        self.state = self.STATE.SYSTEM_GREET
        if "TEACH YOU THE CONCEPT" in response:
          self.state = self.STATE.TUTORING_BEGIN
          obj_schema = self.read_from_eta(mode = "GOAL_REQ")
          print ("GOAL: ", obj_schema)					
          #print ("OBJ_SCHEMA: ", obj_schema)
          self.planner.init(obj_schema)
          goal_schema = self.planner.get_goal_schema()
          print ("GOAL SCHEMA: ", goal_schema)
          self.send_to_eta(mode="GOAL_RESP", text=goal_schema)
          next_step = self.planner.next()
          print ("NEXT STEP:", next_step)
          #self.send_to_eta(mode="PLAN_STEP", text=next_step)

        else:
          print ("Go ahead, ask a question...")
        continue

      self.current_input = input ("\033[1;34;40mYOU: ")
      print ("\033[0;37;40m")

      if self.current_input != "":
        
        if self.state != self.STATE.SUSPEND and self.state != self.STATE.TUTORING_BEGIN:
          self.state = self.STATE.QUESTION_PENDING

        # Unnecessary without audio input
        # self.current_input = self.preprocess(self.current_input)
        
        if self.state != self.STATE.SUSPEND:

          self.qa()
          
          if response is not None and ("good bye" in response.lower() or "take a break" in response.lower()):
            print ("ENDING THE SESSION...")
            exit()

          time.sleep(0.5)					
        self.current_input = ""
      time.sleep(0.1)

  def qa(self):
    time.sleep(0.2)										
    self.send_to_eta("INPUT", self.current_input)
    self.send_perceptions()
    time.sleep(1.0)

    #print ("WAITING FOR ULF...")
    ulf = self.read_from_eta(mode = "ULF")
    
    #print ("RETURNED ULF FROM ETA: ", ulf)
    if ulf is not None and ulf != "":
      if 'NON-QUERY' not in ulf.upper():
        response_surface = self.process_spatial_request(ulf)							
        print ("Sending Response to ETA: " + response_surface)										
        self.send_to_eta("ANSWER", response_surface)
    time.sleep(4.0)
    
    response = str(self.read_and_vocalize_from_eta())
    open(self.eta_answer, 'w').close()
    self.dialog_counter += 1

  def process_spatial_request(self, ulf):
    response_surface = "\'None"
    if ulf is not None and ulf != "" and ulf != "NIL":
      if re.search(r"^\((\:OUT|OUT|OUT:)", ulf):
        if "(OUT " in ulf:
          ulf = (ulf.split("(OUT ")[1])[:-1]
        else:
          ulf = (ulf.split("(:OUT ")[1])[:-1]
        response_surface = ulf
      else:
        self.state = self.STATE.QUESTION_PENDING
        try:
          print ("ULF: ", ulf, self.last_mentioned)
          if "IT.PRO" in ulf and self.last_mentioned is not None and len(self.last_mentioned) > 0:
            ulf = ulf.replace("IT.PRO", self.last_mentioned[0].get_ulf())
          POSS_FLAG = False
          if "POSS-QUES" in ulf:
            POSS_FLAG = True
            ulf = (ulf.split("POSS-QUES ")[1])[:-1]
          query_tree = self.ulf_parser.parse(ulf)					
          query_frame = QueryFrame(self.current_input, ulf, query_tree)
          
          answer_set_rel, answer_set_ref = process_query(query_frame, self.world.entities)
          answer_set_rel = [item for item in answer_set_rel if item[1] > 0.1]

          if answer_set_ref is not None:
            answer_set_ref = [item for item in answer_set_ref if item[1] > 0.1]
          response_surface = self.get_ulf(query_frame, answer_set_rel, answer_set_ref)
        
          if POSS_FLAG:
            response_surface = "POSS-ANS " + response_surface
        except Exception as e:
          query_frame = QueryFrame(None, None, None)					
          response_surface = "\'None"#self.generate_response(query_frame, [], [])
          #print (str(e))
          traceback.print_exc()

    return response_surface


def main():
  manager = HCIManager()
  manager.start()

if __name__== "__main__":
    main()