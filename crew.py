from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434", temperature=0.2, request_timeout=300)

search_tool = SerperDevTool(
    search_url="https://google.serper.dev/search",
    n_results=2,
)

print(search_tool.run(search_query="gcp terraform provider"))

for entry in ENV_VARS.get("ollama", []):
    if "API_BASE" in entry:
        entry["BASE_URL"] = entry.pop("API_BASE")
	    
@CrewBase
class Iac():
	"""Iac crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def script_generator(self) -> Agent:
		return Agent(
			config=self.agents_config['script_generator'],
			verbose=True,
			llm=llm,
			tools=[search_tool]
		)

	@agent
	def script_validator(self) -> Agent:
		return Agent(
			config=self.agents_config['script_validator'],
			verbose=True,
			llm=llm
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def generate_script_task(self) -> Task:
		return Task(
			config=self.tasks_config['generate_script_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)
	
	@task
	def store_script_task(self) -> Task:
		return Task(
			config=self.tasks_config['store_script_task'],
			output_file='report.md'
		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the Iac crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
