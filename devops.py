import base64
import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
import time

load_dotenv()

class DevOpsAssistant:
    def __init__(self):
        self.console = Console()
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-2.5-pro"
        self.conversation_history = []
        
        # Initialize the conversation with system context
        self.conversation_history = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="""You are a Senior DevOps Engineer with 10+ years of experience in debugging production systems, CI/CD pipelines, Docker, Kubernetes, and cloud infrastructure (AWS, Azure, GCP).  
Your primary goal is to analyze logs, error traces, and configuration files to identify issues and suggest precise fixes.  
Your explanations must be clear, direct, and actionable, as if mentoring a junior engineer.  
Always provide:
1. Root cause analysis.
2. Immediate fix or workaround.
3. Long-term preventive measures.
4. Verification steps to confirm the issue is resolved.

- Do not use buzzwords or generic "best practice" lectures unless specifically asked.  
- Always reference commands, configs, or tools concretely.  
- If multiple solutions exist, explain pros/cons.  
- Assume Linux-based environments unless specified.
- Format your responses in markdown for better readability.
"""),
                ],
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text="""Understood. I'm ready to help you debug production issues and provide concrete, actionable solutions.

I'll analyze your logs, configurations, and error traces to:
- Identify root causes
- Suggest immediate fixes
- Provide long-term solutions
- Give you exact commands and verification steps

Send me your production issue, logs, or configuration files. The more context you provide, the better I can help."""),
                ],
            ),
        ]

    def display_banner(self):
        """Display the application banner"""
        banner = Text()
        banner.append("🔧 DevOps Assistant CLI 🔧", style="bold blue")
        banner.append("\n")
        banner.append("Your Senior DevOps Engineer for Production Debugging", style="italic cyan")
        
        self.console.print(Panel(banner, title="Welcome", border_style="blue"))
        self.console.print()

    def display_help(self):
        """Display help information"""
        help_text = """
## Available Commands:

- **help** - Show this help message
- **clear** - Clear conversation history
- **exit** - Exit the application
- **history** - Show conversation history
- **paste** - Enter multi-line input mode (useful for logs/configs)

## Usage Tips:

1. **For Log Analysis**: Paste your error logs directly
2. **For Config Issues**: Share your configuration files
3. **For Debugging**: Describe your problem with as much context as possible
4. **For Commands**: Ask for specific commands or troubleshooting steps

Simply type your question or paste your logs to get started!
        """
        self.console.print(Markdown(help_text))

    def get_multiline_input(self):
        """Get multiline input from user"""
        self.console.print("[yellow]Enter your logs/config (press Ctrl+D or type 'END' on a new line to finish):[/yellow]")
        lines = []
        try:
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines)

    def stream_response(self, user_input):
        """Stream response from Gemini with loading indicator"""
        # Add user input to conversation history
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)]
            )
        )

        # Configure generation
        tools = [types.Tool(googleSearch=types.GoogleSearch())]
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            tools=tools,
            system_instruction=[
                types.Part.from_text(text="""You are a senior DevOps engineer with expertise in cloud infrastructure, CI/CD pipelines, containerization (Docker, Kubernetes), monitoring, observability, and debugging production issues.
Your role is to:

Debugging Mindset:
- Read server logs, error traces, and stack outputs carefully.
- Identify root causes and explain them clearly.
- Suggest actionable fixes (both quick patches and long-term solutions).

Problem-Solving Style:
- Approach problems like a senior engineer mentoring a junior.
- Explain not only the what but also the why.
- Provide step-by-step guidance to reproduce, debug, and resolve issues.

Communication Style:
- Be direct, technical, and precise (no corporate fluff).
- Use code snippets, commands, or configuration examples where useful.
- Assume the user is smart but may need clarity on deeper DevOps concepts.
- Format responses in markdown for better readability.

Context Awareness:
- Support multiple environments (Linux servers, cloud platforms, Docker/K8s clusters).
- Recognize common CI/CD tools (GitHub Actions, Jenkins, GitLab CI, etc.).
- Handle networking, load balancing, scaling, monitoring, and incident response scenarios.

Constraints:
- Avoid unnecessary explanations if a log error is straightforward.
- Always suggest verification steps (e.g., kubectl describe pod, docker logs, journalctl -xe).
- Focus on practical fixes that can be applied immediately."""),
            ],
        )

        response_text = ""
        
        # Show loading spinner
        with Live(Spinner("dots", text="🤔 Analyzing your issue..."), console=self.console):
            try:
                # Generate streaming response
                for chunk in self.client.models.generate_content_stream(
                    model=self.model,
                    contents=self.conversation_history,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        response_text += chunk.text
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
                return

        # Display the response with markdown formatting
        if response_text:
            self.console.print("\n[bold green]🔍 DevOps Analysis:[/bold green]\n")
            self.console.print(Markdown(response_text))
            
            # Add assistant response to conversation history
            self.conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response_text)]
                )
            )
        else:
            self.console.print("[yellow]No response generated. Please try again.[/yellow]")

    def show_history(self):
        """Show conversation history"""
        if len(self.conversation_history) <= 2:  # Only system messages
            self.console.print("[yellow]No conversation history yet.[/yellow]")
            return
            
        self.console.print("[bold blue]📝 Conversation History:[/bold blue]\n")
        
        for i, content in enumerate(self.conversation_history[2:], 1):  # Skip system messages
            if content.role == "user":
                self.console.print(f"[bold cyan]User #{i}:[/bold cyan]")
                self.console.print(f"[cyan]{content.parts[0].text}[/cyan]\n")
            elif content.role == "model":
                self.console.print(f"[bold green]Assistant #{i}:[/bold green]")
                self.console.print(Markdown(content.parts[0].text))
                self.console.print()

    def clear_history(self):
        """Clear conversation history but keep system context"""
        self.conversation_history = self.conversation_history[:2]  # Keep only system messages
        self.console.print("[green]✅ Conversation history cleared![/green]")

    def run(self):
        """Main application loop"""
        # Check if API key exists
        if not os.getenv("GEMINI_API_KEY"):
            self.console.print("[red]❌ Error: GEMINI_API_KEY not found in environment variables.[/red]")
            self.console.print("[yellow]Please add your Gemini API key to your .env file or environment variables.[/yellow]")
            return

        self.display_banner()
        self.console.print("[dim]Type 'help' for available commands, 'exit' to quit[/dim]\n")

        while True:
            try:
                # Get user input with custom prompt
                user_input = Prompt.ask(
                    "[bold blue]DevOps[/bold blue]",
                    default="",
                ).strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() == "exit":
                    self.console.print("[green]👋 Thanks for using DevOps Assistant! Stay debugging! 🔧[/green]")
                    break
                elif user_input.lower() == "help":
                    self.display_help()
                    continue
                elif user_input.lower() == "clear":
                    self.clear_history()
                    continue
                elif user_input.lower() == "history":
                    self.show_history()
                    continue
                elif user_input.lower() == "paste":
                    user_input = self.get_multiline_input()
                    if not user_input.strip():
                        self.console.print("[yellow]No input provided.[/yellow]")
                        continue

                # Process the user input
                self.stream_response(user_input)
                self.console.print()  # Add spacing

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit properly.[/yellow]")
                continue
            except EOFError:
                self.console.print("\n[green]👋 Goodbye![/green]")
                break
            except Exception as e:
                self.console.print(f"[red]Unexpected error: {str(e)}[/red]")
                continue

def main():
    """Entry point of the application"""
    try:
        assistant = DevOpsAssistant()
        assistant.run()
    except Exception as e:
        console = Console()
        console.print(f"[red]Failed to start DevOps Assistant: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()