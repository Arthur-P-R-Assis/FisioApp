from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from tinydb import TinyDB,Query, where
import os
from kivy.uix.screenmanager import Screen,ScreenManager
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.properties import ObjectProperty
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.uix.label import Label
from kivymd.uix.button import MDIconButton
from kivy.utils import get_color_from_hex
import kivy
import kivymd


if not os.path.exists('venv/fisioterapia/tabela.json'):
    bd = TinyDB('venv/fisioterapia/tabela.json')

class LoginScreen(Screen):

#############################################################################################################################################
#######################################################################LOGIN##################################################################
#############################################################################################################################################
    def verificar_atualizar_tabela(self,login):
        db = TinyDB('venv/fisioterapia/tabela.json')

        if 'logado' in db.tables():
            logado_table = db.table('logado')
            logado_table.update({'logado': str(login)})
        else:
            nova_table = db.table(login)
            logado_table = db.table('logado')
            logado_table.insert({'logado': str(login)})

            db.close()
    
    def obter_usuario_logado(self):
        db = TinyDB('venv/fisioterapia/tabela.json')
        logado_table = db.table('logado')

        logado_user = logado_table.get(doc_id=1)

        if logado_user:
            usuario_logado = logado_user['logado']
            db.close()
            return usuario_logado
        else:
            db.close()
            return None
 
    def login(self):
        self.app = App.get_running_app()
        login_screen = self.app.sm.get_screen('login')
        login = login_screen.ids.login_field.text
        senha = login_screen.ids.senha_field.text

        db = TinyDB('venv/fisioterapia/tabela.json')
        tables = db.tables()  
        result = None
        for table_name in tables:
            table = db.table(table_name)
            if table.search((Query().Login == login) & (Query().Senha == senha)):
                result = True
                break
    
        db.close()

        if result:
            self.verificar_atualizar_tabela(login)
            self.app.goto_inicial()
            login_screen.ids.login_field.text = ""
            login_screen.ids.senha_field.text = ""

        else:
            login_screen.ids.status_label.text =  "Login ou senha inválidos."
            Clock.schedule_once(self.reset_text, 1)

    def reset_text(self, dt):
        self.app = App.get_running_app()
        login_screen = self.app.sm.get_screen('login')
        login_screen.ids.status_label.text = ""

    def clear_error_messagel(self, dt):
        self.app = App.get_running_app()
        self.app.sm.get_screen('login').ids.status_label.text = ""


#############################################################################################################################################
################################################################Recuperar Senha##############################################################
#############################################################################################################################################
        
    def recover_password(self, email, dialog):
        self.app = App.get_running_app()
        login_screen = self.app.sm.get_screen('login')
        db = None
        try:
            db = TinyDB('venv/fisioterapia/tabela.json')
            users = db.table('usuario')
            user = users.get(where('Login') == email)
            if user:
                new_password = self.generate_random_password()
                users.update({'Senha': new_password}, where('Login') == email)
                if self.send_email(email, new_password):
                    login_screen.ids.status_label.text =  "Sua senha foi enviada para o email."
                else:
                    login_screen.ids.status_label.text =  "Erro ao enviar email. Por favor, tente novamente mais tarde."
            else:
                login_screen.ids.status_label.text =  "Este email não está cadastrado. Por favor, verifique o email digitado."
        except Exception as e:
            login_screen.ids.status_label.text =  "Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde."
        finally:
            Clock.schedule_once(self.reset_text, 3)
            dialog.dismiss()
            if db:
                db.close()

    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def send_email(self, email, new_password):
        try:
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender_email = 'arthurpaivaassis@gmail.com'
            sender_password = 'zutertciiazfvqqu'

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = 'Recuperação de Senha'

            body = f'Sua nova senha é: {new_password}'
            msg.attach(MIMEText(body, 'plain'))
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
            server.quit()

            return True

        except Exception as e:
            print("Ocorreu um erro ao enviar o email:", str(e))
            return False
        
    def show_alert_dialog(self):
        self.app = App.get_running_app()
        email_field = MDTextField()
        
        dialog = MDDialog(
            title="Digite seu email: ",
            type="custom",
            content_cls=email_field,
            buttons=[
                MDFlatButton(
                    text="Recuperar",
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda *args: self.recover_password(email_field.text,dialog)
                ),
                MDFlatButton(
                    text="voltar", 
                    text_color=self.app.theme_cls.primary_color,
                    on_release=lambda *args: dialog.dismiss()
                )
            ]
        )
        dialog.open()

class RegisterScreen(Screen):
    def register(self):
        self.app = App.get_running_app()
        name = self.app.sm.get_screen('register').ids.name_field.text
        login = self.app.sm.get_screen('register').ids.email_field.text
        password = self.app.sm.get_screen('register').ids.senha_field.text
        register_screen = self.app.sm.get_screen('register')

        db = TinyDB('venv/fisioterapia/tabela.json')
        tables = db.tables()
        result = False  
        tabela_usuario =db.table('usuario')

        for table_name in tables:
            table = db.table(table_name)

            if table.search(Query().Login == login):
                result = True  
                break

        if result:
            register_screen.ids.error_label.text = "Email já Cadastrado."
            Clock.schedule_once(self.clear_error_message, 2)
            self.app.sm.get_screen('register').ids.name_field.text = ""
            self.app.sm.get_screen('register').ids.email_field.text = ""
            self.app.sm.get_screen('register').ids.senha_field.text = ""

        else:
            dados = {'Login': str(login), 'Senha': str(password), 'Nome': str(name)}
            tabela_usuario.insert(dados)
            register_screen.ids.error_label.text = "Cadastro feito com sucesso."
            Clock.schedule_once(self.clear_error_message, 2)
            self.app.sm.get_screen('register').ids.name_field.text = ""
            self.app.sm.get_screen('register').ids.email_field.text = ""
            self.app.sm.get_screen('register').ids.senha_field.text = ""
            
        db.close()
    
    def clear_error_message(self, dt):
        self.app = App.get_running_app()
        self.app.sm.get_screen('register').ids.error_label.text = ""

class InicialScreen(Screen):
    bd = TinyDB('venv/fisioterapia/tabela.json')
    app = ObjectProperty()  # Adicione essa linha

    def __init__(self, app=None, **kwargs):
        super(InicialScreen, self).__init__(**kwargs)
        self.app = app
        self.ficha_screen = FichaScreen()
        self.info_screen = InfoScreen()
        self.login_screen = LoginScreen()
        self.login = self.login_screen.obter_usuario_logado()

    def on_pre_enter(self):
        self.load_items()

    def goto_ficha(self, nome, ficha_screen):
        if self.app and hasattr(self.app, 'sm') and self.app.sm:
            self.app.sm.current = 'ficha'
            ficha_screen.carregar_dados(nome)
    
    def goto_info(self, nome,info_screen):
        if self.app and hasattr(self.app, 'sm') and self.app.sm:
            info_screen.carregar_dados(nome)
            self.app.sm.current = 'info'

    def add_item(self, message):

        item_layout = BoxLayout(size_hint_y=None, height=dp(50), orientation='horizontal')  # Orientação horizontal

        # Adiciona a mensagem no lado esquerdo
        item_label = Label(text=message, color=get_color_from_hex('#333333'), halign='center',valign='middle')
        item_label.bind(size=item_label.setter('text_size'))  # Define a cor do texto como cinza e
        item_layout.add_widget(item_label)

        # Adiciona um widget spacer para separar a mensagem dos ícones
        item_layout.add_widget(Widget())

        # Adiciona os ícones nos botões no canto direito
        icons = ["eye", "pencil", "delete"]  # Ícones para olho, lápis e lixeira
        for icon_name in icons:
            if icon_name == "delete":
                # Adiciona o botão de lixeira com evento de exclusão da linha correspondente
                button = MDIconButton(icon=icon_name)
                button.bind(on_release=lambda btn, name=message: self.delete_item(name))

            elif icon_name == 'eye':
                button = MDIconButton(icon=icon_name)
                button.bind(on_release=lambda instance, name=message: self.goto_ficha(name, self.app.sm.get_screen('ficha')))

            else:
                button = MDIconButton(icon=icon_name)
                button.bind(on_release=lambda instance, name=message: self.goto_info(name,self.app.sm.get_screen('info')))
            item_layout.add_widget(button)

        # Adiciona a faixa horizontal na grade de itens
        self.ids.items_grid.add_widget(item_layout)

    def delete_item(self, name, login):
        # Remove a linha correspondente ao nome da tabela 'paciente' do usuário logado
        self.bd.table(login).remove(where('nome') == name)
        # Atualiza a grade de itens após a exclusão
        self.update_items_grid()

    def update_items_grid(self):

        self.ids.items_grid.clear_widgets()

        login = self.login_screen.obter_usuario_logado()
        if login:
            # Itera sobre os itens da tabela do usuário logado
            for item in self.bd.table(login).all():
                # Verifica se a chave 'nome' está presente no item
                if 'nome' in item:
                    # Adiciona apenas o valor associado à chave 'nome'
                    message = item['nome']
                    
                    # Cria um layout para o item
                    item_layout = BoxLayout(size_hint_y=None, height=dp(50), orientation='horizontal')  # Orientação horizontal
                    
                    # Adiciona a mensagem como Label com a cor cinza escuro
                    item_label = Label(text=message, color=get_color_from_hex('#333333'), halign='center',valign='middle')
                    item_label.bind(size=item_label.setter('text_size'))  # Define a cor do texto como cinza e
                    item_layout.add_widget(item_label)
                    
                    # Adiciona um widget spacer para separar a mensagem dos ícones
                    item_layout.add_widget(Widget())
                    
                    # Adiciona os ícones nos botões no canto direito
                    icons = ["eye", "pencil", "delete"]  # Ícones para olho, lápis e lixeira
                    for icon_name in icons:
                        if icon_name == "delete":
                            # Adiciona o botão de lixeira com evento de exclusão da linha correspondente
                            button = MDIconButton(icon=icon_name)
                            button.bind(on_release=lambda btn, name=message: self.delete_item(name, login))
    
                        elif icon_name == 'eye':
                            button = MDIconButton(icon=icon_name)
                            button.bind(on_release=lambda instance, name=message: self.goto_ficha(name, self.app.sm.get_screen('ficha')))
    
                        else:
                            button = MDIconButton(icon=icon_name)
                            button.bind(on_release=lambda instance, name=message: self.goto_info(name, self.app.sm.get_screen('info')))
                        
                        item_layout.add_widget(button)
                    
                    # Adiciona o layout do item à grade de itens
                    self.ids.items_grid.add_widget(item_layout)
        else:
            # Se não houver usuário logado, limpa a grade de itens
            self.ids.items_grid.clear_widgets()
    def load_items(self):
        self.update_items_grid()

class InfoScreen(Screen):
    def __init__(self, app=None, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.current_index = 0
        self.app = app
        self.login_screen = LoginScreen()  
        self.login = self.login_screen.obter_usuario_logado()  
        self.db = TinyDB('venv/fisioterapia/tabela.json')
        self.fields = [
            "Nome", "Endereço", "Contato", "Data de Nascimento", "Data de Avaliação", "Fisioterapeuta",
            "Campo", "Condição", "Queixa", "Fatores Pessoais", "Fatores Ambientais",
            "Limitações", "Deficiências", "Diagnóstico", "Objetivos", "Condutas", "Comentários"
        ]
        self.data_list = []  # Lista para armazenar os textos preenchidos
        self.dados = []

    def on_pre_enter(self):
        if not self.dados:
            self.reset_fields()
        else:
            for i in self.dados:
                self.data_list.append(i)

            self.current_index = 0
            self.ids.current_field.hint_text = self.fields[0]
            self.ids.current_field.text = self.dados[self.current_index]
            self.ids.next_button.text = "Próximo"
            self.current_index += 1

    def add_field(self):
        if not self.dados:
            if self.current_index < (len(self.fields)-1) :
                field_name = self.fields[self.current_index+1]
                self.ids.current_field.hint_text = field_name
                self.ids.current_field.text = ""
                self.current_index += 1
                self.ids.next_button.text = "Salvar" if self.current_index == (len(self.fields)-1) else "Próximo"

        else:
            if self.current_index < (len(self.fields)) :
                field_name = self.fields[self.current_index]
                self.ids.current_field.hint_text = field_name
                self.ids.current_field.text = self.dados[self.current_index]
                self.current_index += 1
                self.ids.next_button.text = "Salvar" if self.current_index == (len(self.fields)) else "Próximo"

    def go_back(self):
        if self.current_index > 0:
            if not self.dados:
                self.current_index -= 1
                field_name = self.fields[self.current_index]
                self.ids.current_field.hint_text = field_name
                self.ids.current_field.text = ""  
                self.ids.next_button.text = "Próximo"
                self.data_list.pop()
            else:
                self.current_index -= 1
                field_name = self.fields[self.current_index]
                self.ids.current_field.hint_text = field_name
                self.ids.current_field.text =  self.dados[self.current_index]
                self.ids.next_button.text = "Próximo"
                self.data_list[self.current_index] = self.ids.current_field.text
                

        else:
            if self.dados:
                table_name = str(self.login)
                paciente = {
                        'nome': self.dados[0],
                        'endereco': self.dados[1],
                        'contato': self.dados[2],
                        'data_nascimento': self.dados[3],
                        'data_de_avaliacao': self.dados[4],
                        'fisioterapeuta': self.dados[5],
                        'campo': self.dados[6],
                        'condicao': self.dados[7],
                        'queixa': self.dados[8],
                        'fatoresp': self.dados[9],
                        'fatoresa': self.dados[10],
                        'limitacoes': self.dados[11],
                        'deficiencias': self.dados[12],
                        'diagnostico': self.dados[13],
                        'objetivos': self.dados[14],
                        'condutas': self.dados[15],
                        'comentarios': self.dados[16],
                    }
                self.db.table(table_name).insert(paciente)
                
            self.data_list = []
            self.dados = []
            self.reset_fields()
            self.app.goto_inicial()

    def save_to_database(self):
        table_name = str(self.login)  
        paciente = {
            'nome': self.data_list[0],
            'endereco': self.data_list[1],
            'contato': self.data_list[2],
            'data_nascimento': self.data_list[3],
            'data_de_avaliacao': self.data_list[4],
            'fisioterapeuta':self.data_list[5],
            'campo': self.data_list[6],
            'condicao': self.data_list[7],
            'queixa': self.data_list[8],
            'fatoresp': self.data_list[9],
            'fatoresa': self.data_list[10],
            'limitacoes': self.data_list[11],
            'deficiencias': self.data_list[12],
            'diagnostico': self.data_list[13],
            'objetivos': self.data_list[14],
            'condutas': self.data_list[15],
            'comentarios': self.data_list[16],
        }
        self.db.table(table_name).insert(paciente)
 

    def on_next_button_press(self):
        if not self.dados:
            if self.ids.next_button.text == "Salvar":
                self.data_list.append(self.ids.current_field.text)
                self.save_to_database()
                self.app.goto_inicial()
                self.data_list = []
                self.dados = []

            else:
                self.data_list.append(self.ids.current_field.text)
                self.add_field()

        else:
            if self.ids.next_button.text == "Salvar":
                self.data_list[self.current_index] = self.ids.current_field.text
                self.save_to_database()
                self.app.goto_inicial()
                self.data_list = []
                self.dados = []

            else:
                self.add_field()

    def reset_fields(self):
        self.current_index = 0
        self.ids.current_field.hint_text = self.fields[0]
        self.ids.current_field.text = ""  # Limpa o texto do campo atual
        self.ids.next_button.text = "Próximo"

    def carregar_dados(self, nome):
        paciente = Query()
        result = self.db.table(self.login).get(paciente.nome == nome)
        if result:
            self.dados.append(result['nome'])
            self.dados.append(result['endereco'])
            self.dados.append(result['contato'])
            self.dados.append(result['data_nascimento'])
            self.dados.append(result['data_de_avaliacao'])
            self.dados.append(result['fisioterapeuta'])
            self.dados.append(result['campo'])
            self.dados.append(result['condicao'])
            self.dados.append(result['queixa'])
            self.dados.append(result['fatoresp'])
            self.dados.append(result['fatoresa'])
            self.dados.append(result['limitacoes'])
            self.dados.append(result['deficiencias'])
            self.dados.append(result['diagnostico'])
            self.dados.append(result['objetivos'])
            self.dados.append(result['condutas'])
            self.dados.append(result['comentarios'])

            self.app.sm.get_screen('inicial').delete_item(nome,self.login)

class FichaScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.login_screen = LoginScreen()
        self.login = self.login_screen.obter_usuario_logado()

    def carregar_dados(self,nome):
        db = TinyDB('venv/fisioterapia/tabela.json')
        paciente = Query()
        result = db.table(self.login).get(paciente.nome == nome)
        db.close()

        if result:
            self.ids.label_nome.text = result['nome']
            self.ids.endereco.text = result['endereco']
            self.ids.contato.text = result['contato']
            self.ids.nascimento.text = result['data_nascimento']
            self.ids.data.text = result['data_de_avaliacao']
            self.ids.fisioterapia.text = result['fisioterapeuta']
            self.ids.campo.text = result['campo']
            self.ids.condicao.text = result['condicao']
            self.ids.queixa.text = result['queixa']
            self.ids.fatoresp.text = result['fatoresp']
            self.ids.fatoresa.text = result['fatoresa']
            self.ids.limitacoes.text = result['limitacoes']
            self.ids.deficiencias.text = result['deficiencias']
            self.ids.diagnostico.text = result['diagnostico']
            self.ids.objetivos.text = result['objetivos']
            self.ids.condutas.text = result['condutas']
            self.ids.comentarios.text = result['comentarios']

class FisioTECHApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'  # Tema claro
        self.theme_cls.primary_palette = 'BlueGray'  # Paleta de cores primárias
        self.theme_cls.primary_hue = '700'

        Builder.load_file('loginscreen.kv')
        Builder.load_file('registerscreen.kv')
        Builder.load_file('inicialscreen.kv')
        Builder.load_file('infoscreen.kv')
        Builder.load_file('fichascreen.kv')

        self.sm = ScreenManager()
        screen_login = LoginScreen(name='login')
        screen_register = RegisterScreen(name='register')
        screen_inicial = InicialScreen(name='inicial', app=self)
        screen_info = InfoScreen(name='info', app=self)
        screen_ficha = FichaScreen(name='ficha')

        self.sm.add_widget(screen_login)
        self.sm.add_widget(screen_register)
        self.sm.add_widget(screen_inicial)
        self.sm.add_widget(screen_info)
        self.sm.add_widget(screen_ficha)
        
        return self.sm

    def goto_inicial(self):
        self.sm.current = 'inicial'

    def goto_login(self):
        self.sm.current = 'login'
    
    def goto_register(self):
        self.sm.current = 'register'

    def goto_info(self):
        self.sm.current = 'info'

    def goto_ficha(self):
        self.sm.current = 'ficha'
            
if __name__ == '__main__':
    FisioTECHApp().run()
    print("Versão do Kivy:", kivy.__version__)
    print("Versão do KivyMD:", kivymd.__version__)