CodeSystem: SGTasks
Title:        "SMART Guidelines Tasks"
Description:  """
CodeSystem for SMART Guidelines tasks which are specializations of the Business Process Modeling Notatiton (BPMN) tasks, which are included in this codesystem

See [BPMN Spectification](https://www.omg.org/spec/BPMN) for more info.  The descriptions were adapted from the [normative human readable documentation](https://www.omg.org/spec/BPMN/2.0.2/PDF).
"""

* ^experimental = true
* ^caseSensitive = false
* ^status = #active

* #businessRuleTask "Business Rule Task" """A Business Rule Task provides a mechanism for the Process to provide input to a Business Rules Engine and to get the output of calculations that the Business Rules Engine might provide."""
* #manualTask "Manual Task" """A Manual Task is a Task that is expected to be performed without the aid of any business process execution engine or any application. An example of this could be a telephone technician installing a telephone at a customer location."""
* #receiveTask "Receive Task"  """A Receive Task is a simple Task that is designed to wait for a Message to arrive from an external Participant (relative to the Process). Once the Message has been received, the Task is completed."""
* #scriptTask "Script Task" """A Script Task is executed by a business process engine. The modeler or implementer defines a script in a language that the engine can interpret. When the Task is ready to start, the engine will execute the script. When the script is completed, the Task will also be completed."""
* #sendTask "Send Task" """A Send Task is a simple Task that is designed to send a Message to an external Participant (relative to the Process). Once the Message has been sent, the Task is completed."""
* #serviceTask "Service Task" """A Service Task is a Task that uses some sort of service, which could be a Web service or an automated application.  : The Service Task has exactly one set of inputs and at most one set of outputs."""
* #task "Task"  """A Task is an atomic Activity within a Process flow. A Task is used when the work in the Process cannot be broken down to a finer level of detail. Generally, an end-user and/or applications are used to perform the Task when it is executed"""
* #userTask "User Task" """A User Task is a typical “workflow” Task where a human performer performs the Task with the assistance of a software application and is scheduled through a task list manager of some sort."""
