from neuron.formatting_utils import colored

def test_colored_with_termcolor(monkeypatch):
    # Simula a presença de termcolor
    text = "Hello"
    result = colored(text, color="red", attrs=["bold"])
    assert isinstance(result, str)  # Verifica se a saída é uma string

def test_colored_without_termcolor(monkeypatch):
    # Simula a ausência de termcolor
    with monkeypatch.context() as m:
        m.delattr("neuron.formatting_utils.termcolor", raising=False)
        text = "Hello"
        result = colored(text, color="red", attrs=["bold"])
        assert result == text  # Espera que o texto seja retornado sem formatação
