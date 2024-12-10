from ..capabilities.neuron_capability import NeuronCapability
from ..neurons.base_neuron import BaseNeuron


class ReflectionCapability(NeuronCapability):

    DEFAULT_SYSTEM_MESSAGE = "Reflect on the initial response, identify improvements for accuracy, clarity, and completeness, and refine it accordingly."

    def __init__(
        self,
        neuron: BaseNeuron,
        system_message: str = DEFAULT_SYSTEM_MESSAGE
    ) -> None:
        """

        Args:
            neuron (BaseNeuron): The neuron to which this capability is attached.
        """
        super().__init__()
        self._neuron = neuron
        self._system_message = system_message
        self._oai_system_message = [{"content": system_message, "role": "user"}]
        self.add_to_neuron(neuron)

    def on_add_to_neuron(self, neuron: BaseNeuron):
        neuron.register_hook(hookable_method="process_message_before_send", hook=self._reflection)

    def _reflection(self, sender, message, recipient, silent):
        question = [{"content": recipient.last_message(sender)['content'], "role": "user"}] 
        answer = [{"content": message['content'], "role": "assistant"}]

        all_messages = []
        all_messages.extend(self._neuron._oai_system_message)
        all_messages.extend(question)
        all_messages.extend(answer)
        all_messages.extend(self._oai_system_message)
        
        llm_client = self._neuron.client
        response = llm_client.create(
            context=all_messages, messages=all_messages, cache=None, neuron=self._neuron
        ).choices[0].message.content
    
        return response
