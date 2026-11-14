# UML-диаграммы конвертации объектов

## Диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_converter {
        <<abstract>>
        +convert(field_name: str, value) dict
    }

    class abstract_convert_factory {
        <<abstract>>
        +create(value) abstract_converter
        +convert(source) dict
    }

    class basic_converter {
        +convert(field_name: str, value) dict
    }

    class datetime_converter {
        +convert(field_name: str, value) dict
    }

    class reference_converter {
        -abstract_convert_factory __factory
        +__init__(factory: abstract_convert_factory)
        +convert(field_name: str, value) dict
    }

    class convert_factory {
        -basic_converter __basic_converter
        -datetime_converter __datetime_converter
        -reference_converter __reference_converter
        -list __path
        +create(value) abstract_converter
        +convert(source) dict
        -__convert_object(source) dict
        -__convert_field(field_name: str, value) dict
        -__get_field_names(source) list
    }

    class operation_error

    abstract_converter <|-- basic_converter
    abstract_converter <|-- datetime_converter
    abstract_converter <|-- reference_converter
    abstract_convert_factory <|-- convert_factory

    convert_factory *-- basic_converter
    convert_factory *-- datetime_converter
    convert_factory *-- reference_converter
    reference_converter --> abstract_convert_factory : преобразует вложенный объект
    convert_factory ..> operation_error : циклическая ссылка
```

## Последовательность конвертации

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиент
    participant Factory as convert_factory
    participant Converter as converter
    participant Reference as reference_converter

    Client->>Factory: convert(source)
    Factory->>Factory: __convert_object(source)
    Factory->>Factory: проверить отсутствие цикла
    Factory->>Factory: получить публичные свойства

    loop Для каждого свойства
        Factory->>Factory: __convert_field(field_name, value)

        alt Простое значение
            Factory->>Factory: create(value)
            Factory->>Converter: convert(field_name, value)
            Converter-->>Factory: {field_name: value}
        else Дата и время
            Factory->>Factory: create(value)
            Factory->>Converter: convert(field_name, value)
            Converter-->>Factory: {field_name: ISO 8601}
        else Коллекция
            Factory->>Factory: __convert_field для каждого элемента
        else Ссылка на объект
            Factory->>Factory: create(value)
            Factory->>Reference: convert(field_name, value)
            Reference->>Factory: convert(value) через abstract_convert_factory
            Factory->>Factory: __convert_object(value)
            Factory-->>Reference: вложенный словарь
            Reference-->>Factory: {field_name: dictionary}
        end
    end

    Factory-->>Client: словарь исходной структуры
```

## Десериализация

### Диаграмма классов

```mermaid
classDiagram
    class deserialize_factory {
        -dict __models
        +load(file_name) dict
        +deserialize(source: dict) base_entity
        -__deserialize_model(source, loaded) base_entity
        -__deserialize_value(value, loaded) object
    }

    class base_entity {
        +id str
        +model_type str
        #_restore_id(value: str)
    }

    class range_model {
        +from_dict(data: dict) range_model
    }

    class nomenclature_group_model {
        +from_dict(data: dict) nomenclature_group_model
    }

    class nomenclature_model {
        +from_dict(data: dict) nomenclature_model
    }

    class warehouse_model {
        +from_dict(data: dict) warehouse_model
    }

    class recipe_ingredient_model {
        +from_dict(data: dict) recipe_ingredient_model
    }

    class recipe_model {
        +from_dict(data: dict) recipe_model
    }

    base_entity <|-- range_model
    base_entity <|-- nomenclature_group_model
    base_entity <|-- nomenclature_model
    base_entity <|-- warehouse_model
    base_entity <|-- recipe_ingredient_model
    base_entity <|-- recipe_model
    deserialize_factory ..> range_model : from_dict
    deserialize_factory ..> nomenclature_group_model : from_dict
    deserialize_factory ..> nomenclature_model : from_dict
    deserialize_factory ..> warehouse_model : from_dict
    deserialize_factory ..> recipe_ingredient_model : from_dict
    deserialize_factory ..> recipe_model : from_dict
```

### Загрузка выгрузки хранилища

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиент
    participant Factory as deserialize_factory
    participant Json as json
    participant Model as Класс по model_type

    Client->>Factory: load(file_name)
    Factory->>Json: load(file)
    Json-->>Factory: словарь выгрузки
    Factory->>Factory: создать общий loaded для этой загрузки

    loop Для каждого поля выгрузки
        Factory->>Factory: __deserialize_value(value, loaded)
        Note over Factory: Элементы списков обрабатываются по одному
        opt Значение является словарём модели
            Factory->>Factory: __deserialize_model(source, loaded)
            Factory->>Factory: найти класс по model_type и проверить ID
            alt ID загружен и данные совпадают
                Factory->>Factory: взять готовый объект из loaded
            else ID ещё не встречался
                Factory->>Factory: отметить ID как незавершённый
                Factory->>Factory: рекурсивно восстановить вложенные поля
                Factory->>Model: from_dict(fields)
                Model-->>Factory: объект с исходным ID
                Factory->>Factory: сохранить объект в loaded
            else ID собирается или данные различаются
                Factory-->>Client: validation_error
            end
        end
    end

    Factory-->>Client: словарь с восстановленными моделями
```
