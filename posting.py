from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

CAMINHO_TEXTO = "imgs_and_texts/textos_selecionados.txt"
CAMINHO_IMAGEM = "imgs_and_texts/imagem_1.jpg"
DEBUG_PORT = 9222

if not os.path.exists(CAMINHO_TEXTO):
    raise FileNotFoundError(f"Arquivo não encontrado: {CAMINHO_TEXTO}")
if not os.path.exists(CAMINHO_IMAGEM):
    raise FileNotFoundError(f"Imagem não encontrada: {CAMINHO_IMAGEM}")

with open(CAMINHO_TEXTO, "r", encoding="utf-8") as f:
    TWEET_TEXT = f.read().strip()

if not TWEET_TEXT:
    raise ValueError("O arquivo de texto está vazio")

print(f"Texto carregado: {len(TWEET_TEXT)} caracteres")
print(f"Imagem: {CAMINHO_IMAGEM}")


def connect_to_existing_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")
    
    print(f"Conectando ao Chromium na porta {DEBUG_PORT}...")
    try:
        driver = webdriver.Chrome(options=options)
        print("Conectado ao Chromium existente!")
        print(f"URL atual: {driver.current_url}")
        return driver
    except Exception as e:
        print(f"Erro ao conectar. Execute antes:")
        print(f"   chromium --remote-debugging-port={DEBUG_PORT}")
        raise e


def find_twitter_tab(driver):
    print("Procurando aba do Twitter...")
    
    all_handles = driver.window_handles
    
    for handle in all_handles:
        driver.switch_to.window(handle)
        current_url = driver.current_url
        
        if "x.com" in current_url or "twitter.com" in current_url:
            print(f"Aba do Twitter encontrada: {current_url}")
            return True
    
    print("Nenhuma aba do Twitter encontrada. Abrindo nova...")
    driver.execute_script("window.open('https://x.com/home', '_blank');")
    time.sleep(3)
    driver.switch_to.window(driver.window_handles[-1])
    return True


def post_tweet_with_image(driver, tweet_text, image_path):
    try:
        print("\nIniciando postagem do tweet...")
        
        if "home" not in driver.current_url:
            driver.get("https://x.com/home")
            time.sleep(3)
        
        print("Aguardando campo de texto na home...")
        tweet_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
        )
        
        print("Digitando texto...")
        tweet_box.click()
        time.sleep(0.5)
        tweet_box.send_keys(tweet_text)
        print(f"Texto inserido: {len(tweet_text)} caracteres")
        time.sleep(2)
        
        print("Fazendo upload da imagem...")
        image_input = driver.find_element(By.XPATH, "//input[@type='file' and @accept]")
        image_input.send_keys(os.path.abspath(image_path))
        print(f"Upload enviado: {image_path}")
        
        print("Aguardando upload completar...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='removeMedia']"))
            )
            print("Imagem carregada!")
        except:
            print("Timeout aguardando preview, mas continuando...")
            time.sleep(5)
            try:
                driver.find_element(By.XPATH, "//img[@alt='Image']")
                print("Imagem detectada por método alternativo!")
            except:
                print("Imagem pode não ter carregado corretamente")
        
        time.sleep(2)
        
        print("Procurando botão POSTAR...")
        
        post_button = None
        selectors = [
            "//button[@data-testid='tweetButtonInline']",
            "//button[@data-testid='tweetButton']",
            "//button[.//span[text()='Post']]",
            "//button[.//span[text()='Postar']]",
        ]
        
        for selector in selectors:
            try:
                post_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print(f"Botão encontrado: {selector}")
                break
            except:
                continue
        
        if not post_button:
            print("Procurando botão manualmente...")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "Post" in btn.text or "Postar" in btn.text:
                    post_button = btn
                    print(f"Botão encontrado por texto: '{btn.text}'")
                    break
        
        if not post_button:
            raise Exception("Botão POSTAR não encontrado!")
        
        time.sleep(1)
        
        driver.execute_script("arguments[0].style.border='3px solid red'", post_button)
        driver.save_screenshot("botao_antes_clicar.png")
        print("Screenshot salvo: botao_antes_clicar.png")
        time.sleep(1)
        
        print("Clicando no botão POSTAR...")
        
        click_success = False
        
        try:
            post_button.click()
            click_success = True
            print("Clique normal executado!")
        except Exception as e:
            print(f"Clique normal falhou: {e}")
            
            try:
                driver.execute_script("arguments[0].click();", post_button)
                click_success = True
                print("JavaScript click executado!")
            except Exception as e:
                print(f"JavaScript click falhou: {e}")
                
                try:
                    driver.execute_script("""
                        var evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        arguments[0].dispatchEvent(evt);
                    """, post_button)
                    click_success = True
                    print("dispatchEvent executado!")
                except Exception as e:
                    print(f"Todos os métodos falharam: {e}")
        
        if not click_success:
            raise Exception("Não foi possível clicar no botão Postar")
        
        print("Aguardando tweet ser publicado...")
        time.sleep(5)
        
        driver.save_screenshot("depois_de_postar.png")
        print("Screenshot final: depois_de_postar.png")
        
        try:
            current_url = driver.current_url
            if "compose" not in current_url:
                print("CONFIRMADO: Tweet postado! (voltou ao feed)")
            else:
                print("Ainda está na tela de compose. Verificando...")
        except:
            pass
        
        print("\nPROCESSO CONCLUÍDO!")
        print(f"Texto: {tweet_text[:80]}{'...' if len(tweet_text) > 80 else ''}")
        print(f"Imagem: {os.path.basename(image_path)}")
        print(f"Horário: {time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"\nERRO durante postagem: {e}")
        driver.save_screenshot("erro_postagem.png")
        print("Screenshot de erro: erro_postagem.png")
        raise e


if __name__ == "__main__":
    driver = None
    
    try:
        driver = connect_to_existing_chrome()
        find_twitter_tab(driver)
        post_tweet_with_image(driver, TWEET_TEXT, CAMINHO_IMAGEM)
        
        print("\nAUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\nMantendo navegador aberto por 10 segundos...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\nERRO GERAL: {e}")
        if driver:
            driver.save_screenshot("erro_final.png")
            print("Screenshot: erro_final.png")
        input("\nPressione ENTER para continuar...")
    
    finally:
        print("\nEncerrando (Chromium continuará aberto)...")