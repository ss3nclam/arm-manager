# Описание
Утилиты для менеджмента АРМ'а
- Служба `arm-cleaner.service` для автоматической очистки дисковой памяти **при проблеме отсутствия подключения к АРМ** среды исполнения MS4D из-за быстрого переполнения носителя с небольшим объёмом памяти. Очищает системный журнал, логи и архивы среды исполнения MS4D.
- Утилита `armon` для мониторинга

> [!IMPORTANT]  
> Для работы утилит необходимы:
> - Система **Linux**
> - Установленная утилита **lsof**
> - **Python 3.7+**


# Установка
1. **Скопируйте репозиторий** любым удобным для вас способом. Например:
    ```sh
    sudo git clone 'https://github.com/ss3nclam/arm-manager.git' ~/
    ```

2. *(необязательно)* **Настройте параметры в конфигурационном файле `config.json` по своему усмотрению**:
    - ***max_diskusage_perc*** - максимальный процент использования дисковой памяти, выше которого включается очистка ***(по-умолчанию - 85)***
    - ***inspection_frequency*** - периодичность проверки директории в сек. ***(по-умолчанию - 60)***
    - ***mplc4_path*** - расположение mplc4 ***(по-умолчанию - `/opt/mplc4`)***

3. **Запустите установщик** из загруженного репозитория:
    ```sh
    sudo ~/arm-manager/deploy.sh
    ```

4. **Убедитесь в исправной работе службы**:
    ```sh
    systemctl status arm-cleaner.py
    ```

5. **Убедитесь в исправной работе `armon`**:
    ```sh
    sudo armon --help
    ```

6. *(необязательно)* **Удалите загруженный репозиторий**
