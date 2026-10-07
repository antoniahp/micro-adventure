// There are no accounts yet: the browser creates an anonymous user id and remembers it.

export function getUserId(): string {
  let userId = localStorage.getItem("userId");
  if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem("userId", userId);
  }
  return userId;
}

export const currentWalk = {
  get: () => localStorage.getItem("walkId"),
  set: (walkId: string) => localStorage.setItem("walkId", walkId),
  clear: () => localStorage.removeItem("walkId"),
};
