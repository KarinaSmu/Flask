import requests
import time
import concurrent.futures
import asyncio
import aiohttp
import argparse




'''
Этот скрипт можно запустить из командной строки, указав список URL-адресов в качестве аргументов. Пример:
python download_images.py https://i.pinimg.com/564x/e1/d2/e5/e1d2e5c04adfe779532bf08d5fd081f6.jpg https://i.pinimg.com/564x/a9/46/97/a9469735730aaaa96c983f01cf3c9bbc.jpg https://i.pinimg.com/564x/c9/68/e1/c968e149b327142b81226bb9733cdd42.jpg
'''




def download_image(url):
    filename = url.split('/')[-1]
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename

async def download_image_async(url, session):
    filename = url.split('/')[-1]
    async with session.get(url) as response:
        with open(filename, 'wb') as f:
            f.write(await response.read())
    return filename

def download_images_threaded(urls):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_image, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            filename = future.result()
            print(f"Downloaded: {filename} in {time.time() - start_time:.2f} seconds")

def download_images_multiprocess(urls):
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(download_image, url) for url in urls]
        for future in concurrent.futures.as_completed(futures):
            filename = future.result()
            print(f"Downloaded: {filename} in {time.time() - start_time:.2f} seconds")

async def download_images_async(urls):
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [download_image_async(url, session) for url in urls]
        for task in asyncio.as_completed(tasks):
            filename = await task
            print(f"Downloaded: {filename} in {time.time() - start_time:.2f} seconds")

def main():
    parser = argparse.ArgumentParser(description='Download images from URLs.')
    parser.add_argument('urls', metavar='URL', type=str, nargs='+', help='List of URLs to download images from')
    args = parser.parse_args()

    urls = args.urls

    print("Downloading images using threading:")
    download_images_threaded(urls)

    print("\nDownloading images using multiprocessing:")
    download_images_multiprocess(urls)

    print("\nDownloading images using asyncio:")
    asyncio.run(download_images_async(urls))

if __name__ == "__main__":
    main()
