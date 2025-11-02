import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer';

const url = 'https://commons.wikimedia.org/wiki/Main_Page';
const pastaDestino = path.join('.', 'imgs_and_texts');

if (!fs.existsSync(pastaDestino)) {
    fs.mkdirSync(pastaDestino);
}

async function baixarImagensETexto() {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle2' });
    
    const conteudoTexto = await page.$eval('div.description.en[lang="en"]', el => el.innerText).catch(() => '');
    
    if (conteudoTexto) {
        fs.writeFileSync(path.join(pastaDestino, 'textos_selecionados.txt'), conteudoTexto);
        console.log('Texto salvo com sucesso!');
    }
    
    const imagens = await page.$$eval('#mf-picture-picture img', imgs => imgs.map(img => img.src));
    console.log(`Encontradas ${imagens.length} imagens.`);
    
    for (let i = 0; i < imagens.length; i++) {
        try {
            const imgResp = await page.goto(imagens[i]);
            const buffer = await imgResp.buffer();
            fs.writeFileSync(path.join(pastaDestino, `imagem_${i + 1}.jpg`), buffer);
            console.log(`Imagem salva: imagem_${i + 1}.jpg`);
        } catch (err) {
            console.error('Erro ao baixar imagem:', imagens[i], err);
        }
    }
    
    await browser.close();
    console.log('Todas as imagens foram baixadas!');
}

baixarImagensETexto();