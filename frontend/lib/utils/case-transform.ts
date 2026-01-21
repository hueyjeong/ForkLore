type AnyObject = Record<string, unknown>;

function isObject(value: unknown): value is AnyObject {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

export function transformKeysToSnakeCase<T>(obj: T): T {
  if (Array.isArray(obj)) {
    return obj.map(item => transformKeysToSnakeCase(item)) as T;
  }

  if (isObject(obj)) {
    const result: AnyObject = {};
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const snakeKey = camelToSnake(key);
        result[snakeKey] = transformKeysToSnakeCase(obj[key]);
      }
    }
    return result as T;
  }

  return obj;
}
