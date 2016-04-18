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

@implementation FinderSync

- (instancetype)init {
    self = [super init];

    NSLog(@"%s launched from %@ ; compiled at %s", __PRETTY_FUNCTION__, [[NSBundle mainBundle] bundlePath], __TIME__);

    // Set up the directory we are syncing.
    const char *homeFolderPath = getpwuid(getuid())->pw_dir;
    NSString *targetFolderPath = [NSString stringWithFormat:@"%s/daruma" , homeFolderPath];
    self.myFolderURL = [NSURL fileURLWithPath:targetFolderPath];
    [FIFinderSyncController defaultController].directoryURLs = [NSSet setWithObject:self.myFolderURL];
    NSLog(@"watching folder: %@", targetFolderPath);
    
    // Set up images for our badge identifiers.
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed:  NSImageNameStatusNone ] label:@"Queued" forBadgeIdentifier:@"queued"];
    [[FIFinderSyncController defaultController] setBadgeImage:[NSImage imageNamed: NSImageNameStatusAvailable] label:@"Upload Complete" forBadgeIdentifier:@"complete"];
    
    return self;
}

#pragma mark - Primary Finder Sync protocol methods

- (void)makeRequest {
    NSString *target_url_string = @"http://requestb.in/tfsk9rtf";
    NSURL *target_url = [NSURL URLWithString:target_url_string];
    NSURLSessionDataTask *requestTask = [[NSURLSession sharedSession] dataTaskWithURL:target_url
                                                                      completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
    // 4: Handle response here
    }];
    [requestTask resume];
}

- (void)requestBadgeIdentifierForURL:(NSURL *)url {
    NSPipe *client_out = [NSPipe pipe];
    NSTask *client_task = [[NSTask alloc] init];
    NSString *client_script_path = [[NSBundle mainBundle] pathForResource:@"client" ofType:@"py"];
    [client_task setLaunchPath: @"/usr/bin/env"];
    [client_task setArguments: @[@"python2.7", client_script_path, @(url.fileSystemRepresentation)]];
    [client_task setStandardOutput:client_out];
    [client_task launch];
    [client_task waitUntilExit];
    
    NSFileHandle *read_handle = [client_out fileHandleForReading];
    NSData *read_data = [read_handle readDataToEndOfFile];
    NSString *read_string = [[NSString alloc] initWithData:read_data encoding:NSUTF8StringEncoding];
    
    NSLog(@"got response (%@) for (%@)", read_string, @(url.fileSystemRepresentation));
    
    NSInteger whichBadge = [read_string integerValue];
    NSString* badgeIdentifier = @[@"", @"queued", @"complete"][whichBadge];
    [[FIFinderSyncController defaultController] setBadgeIdentifier:badgeIdentifier forURL:url];
}

@end

