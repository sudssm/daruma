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
    NSMutableSet *_requested;  /* We are only supposed to set badges for files that have been explicitly asked of us, so we store a list of such requests here */
    NSTimer *_pollTimer;
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
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed: NSImageNameStatusPartiallyAvailable] label:@"Queued" forBadgeIdentifier:@"queued"];
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed: NSImageNameStatusAvailable] label:@"Upload Complete" forBadgeIdentifier:@"complete"];
    
    // Set up internal state for later
    _statuses = nil;
    _requested = [[NSMutableSet alloc] init];
    _pollTimer = [NSTimer scheduledTimerWithTimeInterval:1.0 target:self selector:@selector(refreshStatusCache:) userInfo:nil repeats:YES];
    
    return self;
}

/**
 * Returns the app folder path (i.e. "/Users/steve/daruma").
 */
NSString* getAppFolderPath() {
    static NSString *cachedPath = nil;
    if(cachedPath == nil) {
        const char *homeFolderPath = getpwuid(getuid())->pw_dir;
        cachedPath = [NSString stringWithFormat:@"%s/daruma" , homeFolderPath];
    }
    return cachedPath;
}

/**
 * Translates a system path (e.g. "/Users/steve/daruma/path/to/file") to a daruma path (e.g. "path/to/file").
 */
NSString* darumaPathFor(NSString *systemPath) {
    NSUInteger appFolderPathLength = [getAppFolderPath() length];
    if([systemPath length] == appFolderPathLength) {
        return @"";
    } else {
        return [systemPath substringFromIndex:appFolderPathLength + 1];
    }
}

/**
 * Translates a daruma path (e.g. "path/to/file") to a system path (e.g. "/Users/steve/daruma/path/to/file").
 */
NSString* systemPathFor(NSString *darumaPath) {
    if([darumaPath length] > 0) {
        return [NSString stringWithFormat:@"%@/%@", getAppFolderPath(), darumaPath];
    } else {
        return getAppFolderPath();
    }
}

#pragma mark - Primary Finder Sync protocol methods

/**
 * Downloads the file status map from the daruma server and replaces the cached map with the new map.
 * After the cache has been updated, calls the completionHandler.
 */
- (void)refreshStatusCacheWithCallback:(void(^)())completionHandler {
    NSString *target_url_string = @"http://localhost:28962/iconstatus";
    NSURL *target_url = [NSURL URLWithString:target_url_string];
    NSURLSessionDataTask *requestTask = [[NSURLSession sharedSession] dataTaskWithURL:target_url completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
        
        if(data == nil || response == nil || [(NSHTTPURLResponse *)response statusCode] != 200) {
            _statuses = nil;
            return;
        }
        
        NSDictionary *parsed_response = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        
        _statuses = parsed_response;
        
        completionHandler();
    }];
    [requestTask resume];
}

/**
 * Updates the badge for the file at the given location with its status in the cached map.
 */
- (void)refreshBadgeFromCacheForURL:(NSURL *)url {
    if(_statuses == nil) {
        NSLog(@"clearing badge");
        [[FIFinderSyncController defaultController] setBadgeIdentifier:@"" forURL:url];
        return;
    }

    NSString *path = darumaPathFor(url.path);
    NSNumber *status = [_statuses objectForKey:path];
    if(status == nil) {
        [[FIFinderSyncController defaultController] setBadgeIdentifier:@"queued" forURL:url];
    } else {
        [[FIFinderSyncController defaultController] setBadgeIdentifier:@"complete" forURL:url];
    }
}

/**
 * Updates all file from their statuses in the cached map.
 */
- (void)refreshAllBadgesFromCache {
    // Only redraw files that have already been requested
    for(NSURL *requestedUrl in _requested) {
        [self refreshBadgeFromCacheForURL:requestedUrl];
    }
}

/**
 * Updates the cached map from the server and refreshes all badges with the new information.
 */
- (void)refreshStatusCache:(NSTimer *)timer {
    [self refreshStatusCacheWithCallback:^{
        [self refreshAllBadgesFromCache];
    }];
}

- (void) endObservingDirectoryAtURL:(NSURL *)url {
    if([url.path isEqualToString:getAppFolderPath()]) {
        // If we aren't looking at the daruma folder any more, clear the requests cache.
        [_requested removeAllObjects];
    }
}

- (void)requestBadgeIdentifierForURL:(NSURL *)url {
    [_requested addObject:url];
    [self refreshBadgeFromCacheForURL:url];
}

@end

