export interface RequestWithUser extends Express.Request {
    user?: any; // Define the user type as needed
}

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    message?: string;
}

export type MiddlewareFunction = (req: RequestWithUser, res: Express.Response, next: Express.NextFunction) => void;