
import re
from abc import ABC, abstractmethod


class Cliente:
    """Representa o cliente (titular) de uma conta."""

    def __init__(self, nome, email):
        # usa os setters para validar já na criação do objeto
        self.nome = nome
        self.email = email

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not isinstance(valor, str) or valor.strip() == "":
            raise ValueError("O nome não pode ser vazio.")
        self._nome = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", valor):
            raise ValueError(f"E-mail inválido: '{valor}'")
        self._email = valor

    def __str__(self):
        return f"{self.nome} ({self.email})"

    def __repr__(self):
        return f"Cliente(nome='{self.nome}', email='{self.email}')"


class Conta(ABC):
    """Classe abstrata que representa uma conta bancária genérica."""

    def __init__(self, numero, cliente, saldo_inicial=0.0):
        if not isinstance(numero, int) or numero <= 0:
            raise ValueError("O número da conta deve ser um inteiro positivo.")
        self._numero = numero
        self.cliente = cliente
        self.saldo = saldo_inicial  # passa pelo setter (valida saldo negativo)

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @cliente.setter
    def cliente(self, valor):
        # composição: a conta "tem um" cliente
        if not isinstance(valor, Cliente):
            raise TypeError("O titular da conta deve ser um Cliente.")
        self._cliente = valor

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        if valor < 0:
            raise ValueError("O saldo não pode ser negativo.")
        self._saldo = float(valor)

    def depositar(self, valor):
        """Adiciona um valor positivo ao saldo."""
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser maior que zero.")
        self.saldo = self.saldo + valor

    def sacar(self, valor):
        """Retira um valor do saldo, se houver saldo suficiente."""
        if valor <= 0:
            raise ValueError("O valor do saque deve ser maior que zero.")
        if valor > self.saldo:
            raise ValueError("Saldo insuficiente para o saque.")
        self.saldo = self.saldo - valor

    @abstractmethod
    def fechar_mes(self):
        """Cada tipo de conta faz o fechamento do mês de um jeito."""
        pass

    def __str__(self):
        return f"Conta {self.numero} | {self.cliente.nome} | Saldo: R$ {self.saldo:.2f}"

    def __repr__(self):
        return f"{self.__class__.__name__}(numero={self.numero}, saldo={self.saldo})"

    def __eq__(self, outro):
        # duas contas são iguais se tiverem o mesmo número
        if not isinstance(outro, Conta):
            return NotImplemented
        return self.numero == outro.numero

    def __lt__(self, outro):
        # permite ordenar contas pelo saldo
        return self.saldo < outro.saldo

    def __hash__(self):
        return hash(self.numero)


class ContaCorrente(Conta):
    """Conta corrente: cobra tarifa mensal."""

    def __init__(self, numero, cliente, saldo_inicial=0.0, tarifa=15.0):
        super().__init__(numero, cliente, saldo_inicial)
        if tarifa < 0:
            raise ValueError("A tarifa não pode ser negativa.")
        self.tarifa = tarifa

    def fechar_mes(self):
        """Desconta a tarifa mensal, se houver saldo."""
        if self.saldo >= self.tarifa:
            self.saldo = self.saldo - self.tarifa
            print(f"  Conta corrente {self.numero}: tarifa de R$ {self.tarifa:.2f} cobrada.")
        else:
            print(f"  Conta corrente {self.numero}: saldo insuficiente para a tarifa.")

    def __str__(self):
        return "[Corrente] " + super().__str__()


class ContaPoupanca(Conta):
    """Conta poupança: rende juros mensais."""

    def __init__(self, numero, cliente, saldo_inicial=0.0, taxa_rendimento=0.005):
        super().__init__(numero, cliente, saldo_inicial)
        self.taxa_rendimento = taxa_rendimento

    @property
    def taxa_rendimento(self):
        return self._taxa_rendimento

    @taxa_rendimento.setter
    def taxa_rendimento(self, valor):
        if valor < 0 or valor > 1:
            raise ValueError("A taxa de rendimento deve estar entre 0 e 1.")
        self._taxa_rendimento = valor

    def fechar_mes(self):
        """Adiciona o rendimento mensal ao saldo."""
        rendimento = self.saldo * self.taxa_rendimento
        self.saldo = self.saldo + rendimento
        print(f"  Poupança {self.numero}: rendimento de R$ {rendimento:.2f} creditado.")

    def __str__(self):
        return "[Poupança] " + super().__str__()


def main():

    # 1. Criando objetos (5 clientes + 6 contas = 11 instâncias)

    clientes = [
        Cliente("Ana Souza", "ana@email.com"),
        Cliente("Bruno Lima", "bruno@email.com"),
        Cliente("Carla Dias", "carla@email.com"),
        Cliente("Diego Alves", "diego@email.com"),
        Cliente("Elisa Rocha", "elisa@email.com"),
    ]

    contas = [
        ContaCorrente(1001, clientes[0], 1000),
        ContaPoupanca(1002, clientes[0], 5000),
        ContaCorrente(1003, clientes[1], 200),
        ContaPoupanca(1004, clientes[2], 800, taxa_rendimento=0.01),
        ContaCorrente(1005, clientes[3], 10),
        ContaPoupanca(1006, clientes[4], 3000),
    ]

    print("=== Contas criadas ===")
    for conta in contas:
        print(conta)


    # 2. Polimorfismo: mesma chamada, comportamentos diferentes

    print("\n=== Fechamento do mês (polimorfismo) ===")
    for conta in contas:
        conta.fechar_mes()

    print("\n=== Saldos após o fechamento ===")
    for conta in contas:
        print(conta)


    # 3. Métodos especiais: __lt__, __eq__ e __repr__

    print("\n=== Contas ordenadas por saldo (__lt__) ===")
    for conta in sorted(contas):
        print(repr(conta))

    print(f"\nconta 1001 == conta 1001? {contas[0] == contas[0]}")
    print(f"conta 1001 == conta 1002? {contas[0] == contas[1]}")


    # 4. Tratamento de exceções (entradas inválidas)

    print("\n=== Testes de entradas inválidas ===")

    try:
        contas[0].sacar(999999)
    except ValueError as erro:
        print(f"Erro ao sacar: {erro}")

    try:
        contas[0].depositar(-50)
    except ValueError as erro:
        print(f"Erro ao depositar: {erro}")

    try:
        Cliente("Fulano", "email_invalido")
    except ValueError as erro:
        print(f"Erro ao criar cliente: {erro}")

    try:
        conta_nova = ContaCorrente(2000, clientes[0], -100)
    except ValueError as erro:
        print(f"Erro ao criar conta: {erro}")

    try:
        contas[1].taxa_rendimento = 5
    except ValueError as erro:
        print(f"Erro ao alterar taxa: {erro}")

    try:
        conta_abstrata = Conta(3000, clientes[0])
    except TypeError as erro:
        print(f"Erro ao instanciar classe abstrata: {erro}")


if __name__ == "__main__":
    main()
