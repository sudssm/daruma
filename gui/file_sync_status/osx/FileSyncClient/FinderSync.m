//
//  FinderSync.m
//  FileSyncClient
//
//  Created by Doron Shapiro on 2/7/16.
//  Copyright © 2016 Doron Shapiro. All rights reserved.
//

#include <pwd.h>
#import "FinderSync.h"

@interface FinderSync ()

@property NSURL *myFolderURL;

@end

@implementation FinderSync {
    NSDictionary *_statuses;
}

- (instancetype)init {
    self = [super init];

    NSLog(@"%s launched from %@ ; compiled at %s", __PRETTY_FUNCTION__, [[NSBundle mainBundle] bundlePath], __TIME__);

    // Set up the directory we are syncing.
    NSString *targetFolderPath = getAppFolderPath();
    self.myFolderURL = [NSURL fileURLWithPath:targetFolderPath];
    [FIFinderSyncController defaultController].directoryURLs = [NSSet setWithObject:self.myFolderURL];
    NSLog(@"watching folder: %@", targetFolderPath);
    
    // Set up images for our badge identifiers.
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed:  NSImageNameStatusNone ] label:@"Queued" forBadgeIdentifier:@"queued"];
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed: NSImageNameStatusAvailable] label:@"Upload Complete" forBadgeIdentifier:@"complete"];
    
    return self;
}

NSString* getAppFolderPath() {
    static NSString *cachedPath = nil;
    if(cachedPath == nil) {
        const char *homeFolderPath = getpwuid(getuid())->pw_dir;
        cachedPath = [NSString stringWithFormat:@"%s/daruma" , homeFolderPath];
    }
    return cachedPath;
}

NSString* darumaPathFor(NSString *systemPath) {
    NSUInteger appFolderPathLength = [getAppFolderPath() length];
    if([systemPath length] == appFolderPathLength) {
        return @"";
    } else {
        return [systemPath substringFromIndex:appFolderPathLength + 1];
    }
}

NSString* systemPathFor(NSString *darumaPath) {
    if([darumaPath length] > 0) {
        return [NSString stringWithFormat:@"%@/%@", getAppFolderPath(), darumaPath];
    } else {
        return getAppFolderPath();
    }
}

#pragma mark - Primary Finder Sync protocol methods

- (void)refreshStatusesWithCallback:(void(^)())completionHandler {
    NSString *target_url_string = @"http://localhost:28962/iconstatus";
    NSURL *target_url = [NSURL URLWithString:target_url_string];
    NSURLSessionDataTask *requestTask = [[NSURLSession sharedSession] dataTaskWithURL:target_url completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        
        if(data == nil || response == nil || [(NSHTTPURLResponse *)response statusCode] != 200) {
            return;
        }
        
        NSString *read_string = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
        NSLog(@"got response: (%@)", read_string);
        NSDictionary *parsed_response = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        
        _statuses = parsed_response;
        
        /*for(id path in _statuses) {
            NSNumber *status = [_statuses objectForKey:path];
            NSLog(@"parsed line: %@ %@", path, status);
        }*/
        
        completionHandler();
    }];
    [requestTask resume];
}

- (void)requestBadgeIdentifierForURL:(NSURL *)url {
    NSLog(@"got request for %@", url.path);
    [self refreshStatusesWithCallback:^{
        NSString *darumaUrl = darumaPathFor(url.path);
        NSNumber *statusForFile = [_statuses objectForKey:darumaUrl];
        if(statusForFile == nil) {
            [[FIFinderSyncController defaultController] setBadgeIdentifier:@"queued" forURL:url];
        } else {
            [[FIFinderSyncController defaultController] setBadgeIdentifier:@"complete" forURL:url];
        }
    }];
}

@end

