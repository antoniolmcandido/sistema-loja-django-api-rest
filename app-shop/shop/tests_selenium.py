from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class LoginSeleniumTest(StaticLiveServerTestCase):
    """
    Teste de login usando Selenium com Chrome WebDriver

    Esta classe herda de StaticLiveServerTestCase, que inicia um servidor Django
    de teste em tempo real, permitindo que o Selenium interaja com a aplicação
    como se fosse um usuário real acessando através de um navegador.
    """

    @classmethod
    def setUpClass(cls):
        """
        Método executado UMA VEZ antes de todos os testes da classe.
        Configura o navegador Chrome que será usado em todos os testes.
        """
        super().setUpClass()

        # Configura opções específicas do Chrome WebDriver
        options = webdriver.ChromeOptions()

        # >>> Modo headless: executa o navegador sem interface gráfica (descomente se necessário)
        # options.add_argument('--headless')

        # >>> --no-sandbox: desabilita o sandbox do Chrome (necessário em alguns ambientes de CI/CD)
        # options.add_argument("--no-sandbox")

        # >>> --disable-dev-shm-usage: evita problemas com memória compartilhada em containers Docker
        # options.add_argument("--disable-dev-shm-usage")

        # Inicializa o driver do Chrome com as opções configuradas
        cls.selenium = webdriver.Chrome(options=options)

        # Define um tempo de espera implícito de 10 segundos para encontrar elementos
        # Se um elemento não for encontrado imediatamente, o Selenium aguardará até 10s
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """
        Método executado UMA VEZ após todos os testes da classe.
        Fecha o navegador e libera os recursos.
        """
        cls.selenium.quit()  # Fecha o navegador e encerra a sessão do WebDriver
        super().tearDownClass()

    def setUp(self):
        """
        Método executado ANTES de cada teste individual.
        Cria um usuário de teste no banco de dados para cada execução.
        """
        # Cria um usuário no banco de dados de teste com credenciais conhecidas
        self.user = User.objects.create_user(username="teste", password="1234")

    def test_user_login(self):
        """
        Testa o fluxo completo de login do usuário usando Selenium.

        Este teste simula as ações de um usuário real:
        1. Acessar a página de login
        2. Preencher o formulário com usuário e senha
        3. Submeter o formulário
        4. Verificar se o login foi bem-sucedido através do redirecionamento
        """

        # Navega para a página de login usando a URL do servidor de teste
        # live_server_url é fornecido automaticamente pelo StaticLiveServerTestCase
        self.selenium.get(f"{self.live_server_url}/login/")

        # Localiza os elementos do formulário de login na página HTML
        # By.ID procura elementos pelo atributo 'id' do HTML
        username_input = self.selenium.find_element(By.ID, "username")
        password_input = self.selenium.find_element(By.ID, "password")

        # By.CSS_SELECTOR permite localizar elementos usando seletores CSS
        # Aqui procura um botão com o atributo type="submit"
        submit_button = self.selenium.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )

        # Preenche o campo de usuário digitando o texto
        # send_keys() simula a digitação do usuário no teclado
        username_input.send_keys("teste")

        # Preenche o campo de senha
        password_input.send_keys("1234")

        # Clica no botão de submit para enviar o formulário
        # Isso dispara o processo de autenticação no servidor Django
        submit_button.click()

        # Aguarda até que a URL mude (indicando que houve redirecionamento)
        # WebDriverWait espera até 10 segundos pela condição especificada
        # EC.url_changes verifica se a URL atual é diferente da URL de login
        WebDriverWait(self.selenium, 10).until(
            EC.url_changes(f"{self.live_server_url}/login/")
        )

        # simulando algo, após fazer o login 
        # submit_button_create_user = self.selenium.find_element(
        #     By.ID, 'btn-last-page'
        # )
        # submit_button_create_user.click()

        # Verifica se a URL atual NÃO contém '/login/'
        # Se não contém, significa que o usuário foi redirecionado após login bem-sucedido
        self.assertNotIn("/login/", self.selenium.current_url)

        # Verifica se a URL atual contém o endereço base do servidor
        # Isso confirma que o usuário está em alguma página válida da aplicação
        # (e não em uma página de erro ou URL externa)
        self.assertIn(self.live_server_url, self.selenium.current_url)
 